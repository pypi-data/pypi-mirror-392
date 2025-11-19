#!/usr/bin/env python3
"""
Test metadata coercion and validation on SequencePool.
"""

import pytest

import pandas as pd
from tanat.sequence.base.pool import SequencePool


class TestSequencePoolCoercion:
    """Test that metadata correctly coerce DataFrame dtypes."""

    @pytest.mark.parametrize(
        "seq_type,entity_features,time_columns",
        [
            ("event", ["event_type", "provider"], ["date"]),
            ("state", ["health_state", "condition"], ["start_date", "end_date"]),
            (
                "interval",
                ["medication", "administration_route"],
                ["start_date", "end_date"],
            ),
        ],
    )
    def test_coerce_time_columns_to_datetime(
        self, pool_data, seq_type, entity_features, time_columns
    ):
        """Coerce temporal columns to datetime64[ns]."""
        sequence_data = pool_data[seq_type]

        settings = {
            "id_column": "patient_id",
            "entity_features": entity_features,
            "static_features": ["gender", "age", "insurance", "chronic_condition"],
        }
        if seq_type == "event":
            settings["time_column"] = time_columns[0]
        else:
            settings["start_column"] = time_columns[0]
            settings["end_column"] = time_columns[1]

        pool = SequencePool.init(
            seq_type,
            sequence_data,
            settings=settings,
            static_data=pool_data["static_data"],
        )

        # Verify actual DataFrame columns are datetime
        for col in time_columns:
            assert pd.api.types.is_datetime64_any_dtype(pool.sequence_data[col])

    @pytest.mark.parametrize(
        "seq_type,entity_features,categorical_features",
        [
            ("event", ["event_type", "provider"], ["event_type", "provider"]),
            ("state", ["health_state", "condition"], ["health_state", "condition"]),
            (
                "interval",
                ["medication", "administration_route"],
                ["medication", "administration_route"],
            ),
        ],
    )
    def test_coerce_entity_features_to_categorical(
        self, pool_data, seq_type, entity_features, categorical_features
    ):
        """Coerce entity features to pd.Categorical."""
        sequence_data = pool_data[seq_type]

        settings = {
            "id_column": "patient_id",
            "entity_features": entity_features,
            "static_features": ["gender", "age", "insurance", "chronic_condition"],
        }
        if seq_type == "event":
            settings["time_column"] = "date"
        else:
            settings["start_column"] = "start_date"
            settings["end_column"] = "end_date"

        pool = SequencePool.init(
            seq_type,
            sequence_data,
            settings=settings,
            static_data=pool_data["static_data"],
        )

        # Verify actual DataFrame columns are categorical
        for feature in categorical_features:
            assert isinstance(pool.sequence_data[feature].dtype, pd.CategoricalDtype)

    @pytest.mark.parametrize(
        "static_feature,expected_dtype_check",
        [
            (
                "gender",
                lambda dtype: isinstance(dtype, pd.CategoricalDtype),
            ),
            (
                "age",
                pd.api.types.is_integer_dtype,
            ),
            (
                "insurance",
                lambda dtype: isinstance(dtype, pd.CategoricalDtype),
            ),
            (
                "chronic_condition",
                lambda dtype: isinstance(dtype, pd.CategoricalDtype),
            ),
        ],
    )
    def test_coerce_static_data_dtypes(
        self, pool_data, static_feature, expected_dtype_check
    ):
        """Coerce static data columns to appropriate dtypes."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        # Verify actual DataFrame dtype
        dtype = pool.static_data[static_feature].dtype
        assert expected_dtype_check(
            dtype
        ), f"Column {static_feature} dtype incorrect: {dtype}"

    def test_coerce_numerical_entity_features(self, pool_data):
        """Coerce numerical entity features to numeric dtypes."""
        pool = SequencePool.init(
            "interval",
            pool_data["interval"],
            settings={
                "id_column": "patient_id",
                "start_column": "start_date",
                "end_column": "end_date",
                "entity_features": ["medication", "dosage"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        # Verify DataFrame dtypes
        assert pd.api.types.is_numeric_dtype(pool.sequence_data["dosage"])
        assert isinstance(pool.sequence_data["medication"].dtype, pd.CategoricalDtype)
