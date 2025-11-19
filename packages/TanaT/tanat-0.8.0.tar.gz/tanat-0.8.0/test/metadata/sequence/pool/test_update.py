#!/usr/bin/env python3
"""
Test metadata update methods on SequencePool.
"""

import pytest

import pandas as pd
from tanat.sequence.base.pool import SequencePool


class TestSequencePoolUpdate:
    """Test metadata update methods following notebook examples."""

    # --- Temporal metadata updates ---

    @pytest.mark.parametrize(
        "timezone",
        ["Europe/Paris", "UTC", "America/New_York", "Asia/Tokyo"],
    )
    def test_update_temporal_timezone(self, pool_data, timezone, snapshot):
        """Update timezone setting and verify metadata snapshot."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        pool.update_temporal_metadata(timezone=timezone)

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    @pytest.mark.parametrize(
        "date_format",
        ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"],
    )
    def test_update_temporal_format(self, pool_data, date_format, snapshot):
        """Update date format setting and verify metadata snapshot."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        pool.update_temporal_metadata(format=date_format)

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    def test_update_temporal_multiple_settings(self, pool_data, snapshot):
        """Update multiple temporal settings at once and verify snapshot."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        pool.update_temporal_metadata(timezone="UTC", format="%Y-%m-%d %H:%M:%S")

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    # --- Entity metadata updates ---

    @pytest.mark.parametrize(
        "feature_name,categories,ordered",
        [
            ("event_type", ["CONSULTATION", "EMERGENCY", "EXAM"], True),
            ("provider", ["NURSE", "GENERAL_PRACTITIONER", "SPECIALIST"], False),
        ],
    )
    def test_update_entity_categorical_to_ordered(
        self, pool_data, feature_name, categories, ordered, snapshot
    ):
        """Update entity feature to ordered categorical and verify DataFrame coercion."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        pool.update_entity_metadata(
            feature_name=feature_name,
            feature_type="categorical",
            categories=categories,
            ordered=ordered,
        )

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)
        # Verify DataFrame dtype reflects update
        assert isinstance(pool.sequence_data[feature_name].dtype, pd.CategoricalDtype)
        assert list(pool.sequence_data[feature_name].dtype.categories) == categories
        assert pool.sequence_data[feature_name].dtype.ordered == ordered

    @pytest.mark.parametrize(
        "numeric_categories",
        [[1, 2, 3, 4, 5], [10, 100, 500, 1000]],
    )
    def test_update_entity_numeric_categories_coerced_to_strings(
        self, pool_data, numeric_categories, snapshot
    ):
        """Numeric categories converted to strings + verify DataFrame coercion."""
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

        pool.update_entity_metadata(
            feature_name="dosage",
            feature_type="categorical",
            categories=numeric_categories,
            ordered=True,
        )

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)
        # Verify DataFrame dtype: dosage now categorical with string categories
        assert isinstance(pool.sequence_data["dosage"].dtype, pd.CategoricalDtype)
        expected_categories = [str(c) for c in numeric_categories]
        assert (
            list(pool.sequence_data["dosage"].dtype.categories) == expected_categories
        )
        assert pool.sequence_data["dosage"].dtype.ordered is True

    def test_update_entity_affects_sequence_data_dtype(self, pool_data, snapshot):
        """Verify that entity update changes sequence_data DataFrame dtype."""
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

        # Initially: dosage is numerical
        assert pd.api.types.is_numeric_dtype(pool.sequence_data["dosage"])

        # Update: change dosage from numerical to categorical
        pool.update_entity_metadata(
            feature_name="dosage",
            feature_type="categorical",
            categories=["1", "2", "3"],
            ordered=True,
        )

        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)
        # After update: dosage is categorical
        assert isinstance(pool.sequence_data["dosage"].dtype, pd.CategoricalDtype)
        assert pool.sequence_data["dosage"].dtype.ordered is True

    # --- Static metadata updates ---

    def test_update_static_metadata_affects_static_data_dtype(
        self, pool_data, snapshot
    ):
        """Verify that static metadata update changes static_data DataFrame dtype."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        # Initially: age is numerical (int)
        # Update: change age from numerical to categorical
        pool.update_static_metadata(
            feature_name="age",
            feature_type="categorical",
            categories=["0-18", "19-35", "36-50", "51+"],
            ordered=True,
        )

        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)
        # After update: age is categorical
        assert isinstance(pool.static_data["age"].dtype, pd.CategoricalDtype)
        assert pool.static_data["age"].dtype.ordered is True

    # --- Method chaining ---

    def test_update_method_chaining(self, pool_data, snapshot):
        """Test fluent API with chained updates like in notebook."""
        pool = SequencePool.init(
            "event",
            pool_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=pool_data["static_data"],
        )

        # fmt: off
        result = (
            pool
            .update_temporal_metadata(timezone="UTC")
            .update_entity_metadata(
                feature_name="event_type",
                feature_type="categorical",
                ordered=True
            )
            .update_temporal_metadata(format="%Y-%m-%d")
        )
        # fmt: on

        # Should return self for chaining
        assert result is pool
        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)
