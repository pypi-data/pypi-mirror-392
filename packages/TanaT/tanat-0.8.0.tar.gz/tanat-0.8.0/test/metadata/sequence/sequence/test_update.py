#!/usr/bin/env python3
"""
Test metadata update methods on single sequences.
"""

import pytest
import pandas as pd
from tanat.sequence.base.pool import SequencePool


class TestSingleSequenceUpdate:
    """Test metadata update methods for individual sequences."""

    @pytest.mark.parametrize(
        "timezone",
        ["Europe/Paris", "UTC", "America/New_York", "Asia/Tokyo"],
    )
    def test_update_temporal_timezone(self, single_id_data, timezone, snapshot):
        """Update timezone setting and verify metadata snapshot for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        pool.update_temporal_metadata(timezone=timezone)

        # Verify metadata updated
        assert pool.metadata.temporal_descriptor.settings.timezone == timezone

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    @pytest.mark.parametrize(
        "date_format",
        ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"],
    )
    def test_update_temporal_format(self, single_id_data, date_format, snapshot):
        """Update date format setting and verify metadata snapshot for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        pool.update_temporal_metadata(format=date_format)

        # Verify metadata updated
        assert pool.metadata.temporal_descriptor.settings.format == date_format

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    def test_update_temporal_multiple_settings(self, single_id_data, snapshot):
        """Update multiple temporal settings at once for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        pool.update_temporal_metadata(timezone="UTC", format="%Y-%m-%d %H:%M:%S")

        # Verify metadata updated
        assert pool.metadata.temporal_descriptor.settings.timezone == "UTC"
        assert pool.metadata.temporal_descriptor.settings.format == "%Y-%m-%d %H:%M:%S"

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
        self, single_id_data, feature_name, categories, ordered, snapshot
    ):
        """Update entity feature to ordered categorical for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        pool.update_entity_metadata(
            feature_name=feature_name,
            feature_type="categorical",
            categories=categories,
            ordered=ordered,
        )

        # Verify metadata updated
        descriptor = pool.metadata.entity_descriptors[feature_name]
        assert descriptor.feature_type == "categorical"
        assert descriptor.settings.categories == categories
        assert descriptor.settings.ordered == ordered

        # Verify DataFrame dtype reflects update
        assert isinstance(pool.sequence_data[feature_name].dtype, pd.CategoricalDtype)
        assert list(pool.sequence_data[feature_name].dtype.categories) == categories
        assert pool.sequence_data[feature_name].dtype.ordered == ordered

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    @pytest.mark.parametrize(
        "numeric_categories",
        [[1, 2, 3, 4, 5], [10, 100, 500, 1000]],
    )
    def test_update_entity_numeric_categories_coerced_to_strings(
        self, single_id_data, numeric_categories, snapshot
    ):
        """Numeric categories converted to strings for single sequence."""
        pool = SequencePool.init(
            "interval",
            single_id_data["interval"],
            settings={
                "id_column": "patient_id",
                "start_column": "start_date",
                "end_column": "end_date",
                "entity_features": ["medication", "dosage"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        pool.update_entity_metadata(
            feature_name="dosage",
            feature_type="categorical",
            categories=numeric_categories,
            ordered=True,
        )

        # Verify metadata: numeric categories converted to strings
        descriptor = pool.metadata.entity_descriptors["dosage"]
        expected_categories = [str(c) for c in numeric_categories]
        assert descriptor.settings.categories == expected_categories

        # Verify DataFrame dtype: dosage now categorical with string categories
        assert isinstance(pool.sequence_data["dosage"].dtype, pd.CategoricalDtype)
        assert (
            list(pool.sequence_data["dosage"].dtype.categories) == expected_categories
        )
        assert pool.sequence_data["dosage"].dtype.ordered is True

        # Snapshot complete metadata structure
        snapshot.assert_match(pool.metadata)

    def test_update_entity_affects_sequence_data_dtype(self, single_id_data, snapshot):
        """Verify that entity update changes sequence_data DataFrame dtype for single sequence."""
        pool = SequencePool.init(
            "interval",
            single_id_data["interval"],
            settings={
                "id_column": "patient_id",
                "start_column": "start_date",
                "end_column": "end_date",
                "entity_features": ["medication", "dosage"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
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

        # After update: dosage is categorical
        assert isinstance(pool.sequence_data["dosage"].dtype, pd.CategoricalDtype)
        assert pool.sequence_data["dosage"].dtype.ordered is True

        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)

    # --- Static metadata updates ---

    def test_update_static_metadata_affects_static_data_dtype(
        self, single_id_data, snapshot
    ):
        """Verify that static metadata update changes static_data DataFrame dtype for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
        )

        # Initially: age is numerical (int)
        assert pd.api.types.is_integer_dtype(pool.static_data["age"])

        # Update: change age from numerical to categorical
        pool.update_static_metadata(
            feature_name="age",
            feature_type="categorical",
            categories=["0-18", "19-35", "36-50", "51+"],
            ordered=True,
        )

        # After update: age is categorical
        assert isinstance(pool.static_data["age"].dtype, pd.CategoricalDtype)
        assert pool.static_data["age"].dtype.ordered is True

        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)

    # --- Method chaining ---

    def test_update_method_chaining(self, single_id_data, snapshot):
        """Test fluent API with chained updates for single sequence."""
        pool = SequencePool.init(
            "event",
            single_id_data["event"],
            settings={
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": ["event_type", "provider"],
                "static_features": ["gender", "age", "insurance", "chronic_condition"],
            },
            static_data=single_id_data["static_data"],
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

        # Verify all updates applied
        assert pool.metadata.temporal_descriptor.settings.timezone == "UTC"
        assert pool.metadata.temporal_descriptor.settings.format == "%Y-%m-%d"
        assert pool.metadata.entity_descriptors["event_type"].settings.ordered is True

        # Snapshot final metadata
        snapshot.assert_match(pool.metadata)
