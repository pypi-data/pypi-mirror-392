#!/usr/bin/env python3
"""
Test feature management (add/drop entity features) on sequence pools.
"""

import pytest
import pandas as pd

from tanat.time.granularity import Granularity
from tanat.metadata.descriptor.feature.type.duration import DurationFeatureSettings


class TestAddEntityFeature:
    """
    Tests for add_entity_feature() method on sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_categorical_feature_inferred(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test adding a categorical feature with inferred metadata.
        """
        pool = sequence_pools[pool_type].copy()

        # Create categorical values matching pool length
        values = ["low", "medium", "high"] * (len(pool.sequence_data) // 3)
        values += ["low"] * (len(pool.sequence_data) % 3)

        # Add feature
        result = pool.add_entity_feature("severity", values)

        # Snapshot the sequence result
        snapshot.assert_match(result.sequence_data.to_csv())

        # Snapshot the metadata for the new feature
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_numerical_feature_explicit(self, sequence_pools, pool_type, snapshot):
        """
        Test adding a numerical feature with explicit metadata.
        """
        pool = sequence_pools[pool_type].copy()
        # Create numerical values
        values = [37.5 + i * 0.1 for i in range(len(pool.sequence_data))]

        # Add feature with explicit metadata
        result = pool.add_entity_feature(
            "temperature",
            values,
            metadata={"feature_type": "numerical"},
        )

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_duration_feature_explicit(self, sequence_pools, pool_type, snapshot):
        """
        Test adding a duration feature with explicit metadata and granularity.
        """
        pool = sequence_pools[pool_type].copy()

        # Create duration values
        values = [1, 2, 3, 5] * (len(pool.sequence_data) // 4)
        values += [1] * (len(pool.sequence_data) % 4)

        # Add duration feature with metadata
        result = pool.add_entity_feature(
            "stay_duration",
            values,
            metadata={
                "feature_type": "duration",
                "settings": DurationFeatureSettings(granularity=Granularity.DAY),
            },
        )

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_feature_override_false_raises(self, sequence_pools, pool_type):
        """
        Test that adding an existing feature with override=False raises ValueError.
        """
        pool = sequence_pools[pool_type].copy()

        # Try to add feature that already exists
        existing_feature = pool.settings.entity_features[0]
        values = ["test"] * len(pool.sequence_data)

        with pytest.raises(ValueError):
            pool.add_entity_feature(existing_feature, values, override=False)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_feature_override_true_replaces(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test that adding an existing feature with override=True replaces it.
        """
        pool = sequence_pools[pool_type].copy()

        # Get existing feature and create new values
        existing_feature = pool.settings.entity_features[0]
        new_values = ["replaced"] * len(pool.sequence_data)

        # Override existing feature
        result = pool.add_entity_feature(existing_feature, new_values, override=True)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_feature_wrong_length_raises(self, sequence_pools, pool_type):
        """
        Test that adding a feature with wrong length raises ValueError.
        """
        pool = sequence_pools[pool_type].copy()

        # Create values with wrong length
        wrong_length_values = ["test"] * (len(pool.sequence_data) + 10)

        with pytest.raises(ValueError, match="does not match"):
            pool.add_entity_feature("new_feature", wrong_length_values)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_feature_with_series(self, sequence_pools, pool_type, snapshot):
        """
        Test adding a feature using a pandas Series.
        """
        pool = sequence_pools[pool_type].copy()

        # Create Series with matching length
        values_series = pd.Series(
            ["A", "B", "C"] * (len(pool.sequence_data) // 3)
            + ["A"] * (len(pool.sequence_data) % 3)
        )

        # Add feature
        pool.add_entity_feature("category", values_series)

        # Snapshot the sequence data
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_add_multiple_features_chaining(self, sequence_pools, pool_type, snapshot):
        """
        Test adding multiple features via method chaining.
        """
        pool = sequence_pools[pool_type].copy()

        # Create values
        n = len(pool.sequence_data)
        severity_values = ["low"] * n
        priority_values = [1, 2, 3] * (n // 3) + [1] * (n % 3)

        # Chain multiple adds
        pool.add_entity_feature("severity", severity_values).add_entity_feature(
            "priority", priority_values, metadata={"feature_type": "numerical"}
        )

        # Verify both features added
        # Snapshot the sequence data
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.metadata)


class TestDropEntityFeature:
    """
    Tests for drop_entity_feature() method on sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_drop_existing_feature(self, sequence_pools, pool_type, snapshot):
        """
        Test dropping an existing entity feature.
        """
        pool = sequence_pools[pool_type].copy()
        initial_features = pool.settings.entity_features.copy()

        # Drop first feature (assuming there are multiple)
        feature_to_drop = initial_features[0]
        result = pool.drop_entity_feature(feature_to_drop)

        # Verify method chaining
        assert result is pool

        # Verify feature removed from settings
        assert feature_to_drop not in pool.settings.entity_features
        assert len(pool.settings.entity_features) == len(initial_features) - 1

        # Snapshot the sequence data after drop
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_drop_nonexistent_feature_raises(self, sequence_pools, pool_type):
        """
        Test that dropping a non-existent feature raises ValueError.
        """
        pool = sequence_pools[pool_type].copy()

        with pytest.raises(ValueError, match="not found in entity features"):
            pool.drop_entity_feature("nonexistent_feature")

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_drop_last_feature_raises(self, sequence_pools, pool_type):
        """
        Test that dropping the last entity feature raises ValueError.
        """
        pool = sequence_pools[pool_type].copy()

        # Drop all but one feature
        features = pool.settings.entity_features.copy()
        for feature in features[:-1]:
            pool.drop_entity_feature(feature)

        # Try to drop the last feature
        with pytest.raises(ValueError):
            pool.drop_entity_feature(features[-1])
