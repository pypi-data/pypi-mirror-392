#!/usr/bin/env python3
"""
Test feature management (add/drop entity features) on unique sequences.
"""

import pytest
import pandas as pd

from tanat.time.granularity import Granularity
from tanat.metadata.descriptor.feature.type.duration import DurationFeatureSettings


class TestAddEntityFeature:
    """
    Tests for add_entity_feature() method on unique sequences.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_categorical_feature_inferred(self, sequence_pools, seq_type, snapshot):
        """
        Test adding a categorical feature with inferred metadata.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3].copy()

        # Create categorical values matching sequence length
        n = len(sequence.sequence_data)
        values = ["low", "medium", "high"] * (n // 3) + ["low"] * (n % 3)

        # Add feature
        result = sequence.add_entity_feature("severity", values)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

        # Snapshot the metadata
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_numerical_feature_explicit(self, sequence_pools, seq_type, snapshot):
        """
        Test adding a numerical feature with explicit metadata.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Create numerical values
        n = len(sequence.sequence_data)
        values = [37.5 + i * 0.1 for i in range(n)]

        # Add feature with explicit metadata
        result = sequence.add_entity_feature(
            "temperature",
            values,
            metadata={"feature_type": "numerical"},
        )

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_duration_feature_explicit(self, sequence_pools, seq_type, snapshot):
        """
        Test adding a duration feature with explicit metadata and granularity.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Create duration values
        n = len(sequence.sequence_data)
        values = [1, 2, 3, 5] * (n // 4) + [1] * (n % 4)

        # Add duration feature with metadata
        result = sequence.add_entity_feature(
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

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_feature_override_false_raises(self, sequence_pools, seq_type):
        """
        Test that adding an existing feature with override=False raises ValueError.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Try to add feature that already exists
        existing_feature = sequence.settings.entity_features[0]
        n = len(sequence.sequence_data)
        values = ["test"] * n

        with pytest.raises(ValueError):
            sequence.add_entity_feature(existing_feature, values, override=False)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_feature_override_true_replaces(
        self, sequence_pools, seq_type, snapshot
    ):
        """
        Test that adding an existing feature with override=True replaces it.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Get existing feature and create new values
        existing_feature = sequence.settings.entity_features[0]
        n = len(sequence.sequence_data)
        new_values = ["replaced"] * n

        # Override existing feature
        result = sequence.add_entity_feature(
            existing_feature, new_values, override=True
        )

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_feature_wrong_length_raises(self, sequence_pools, seq_type):
        """
        Test that adding a feature with wrong length raises ValueError.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Create values with wrong length
        n = len(sequence.sequence_data)
        wrong_length_values = ["test"] * (n + 10)

        with pytest.raises(ValueError, match="does not match"):
            sequence.add_entity_feature("new_feature", wrong_length_values)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_feature_with_series(self, sequence_pools, seq_type, snapshot):
        """
        Test adding a feature using a pandas Series.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Create Series with matching length
        n = len(sequence.sequence_data)
        values_series = pd.Series(["A", "B", "C"] * (n // 3) + ["A"] * (n % 3))

        # Add feature
        result = sequence.add_entity_feature("category", values_series)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_multiple_features_chaining(self, sequence_pools, seq_type, snapshot):
        """
        Test adding multiple features via method chaining.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Create values
        n = len(sequence.sequence_data)
        severity_values = ["low"] * n
        priority_values = [1, 2, 3] * (n // 3) + [1] * (n % 3)

        # Chain multiple adds
        result = sequence.add_entity_feature(
            "severity", severity_values
        ).add_entity_feature(
            "priority", priority_values, metadata={"feature_type": "numerical"}
        )

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)


class TestDropEntityFeature:
    """
    Tests for drop_entity_feature() method on unique sequences.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_drop_existing_feature(self, sequence_pools, seq_type, snapshot):
        """
        Test dropping an existing entity feature.
        """
        sequence = sequence_pools[seq_type][3].copy()
        initial_features = sequence.settings.entity_features.copy()

        # Drop first feature (assuming there are multiple)
        feature_to_drop = initial_features[0]
        result = sequence.drop_entity_feature(feature_to_drop)

        # Snapshot the sequence data after drop
        snapshot.assert_match(result.sequence_data.to_csv())
        snapshot.assert_match(result.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_drop_nonexistent_feature_raises(self, sequence_pools, seq_type):
        """
        Test that dropping a non-existent feature raises ValueError.
        """
        sequence = sequence_pools[seq_type][3].copy()

        with pytest.raises(ValueError, match="not found in entity features"):
            sequence.drop_entity_feature("nonexistent_feature")

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_drop_last_feature_raises(self, sequence_pools, seq_type):
        """
        Test that dropping the last entity feature raises ValueError.
        """
        sequence = sequence_pools[seq_type][3].copy()

        # Drop all but one feature
        features = sequence.settings.entity_features.copy()
        for feature in features[:-1]:
            sequence.drop_entity_feature(feature)

        # Try to drop the last feature
        with pytest.raises(ValueError, match="Cannot drop the last entity feature"):
            sequence.drop_entity_feature(features[-1])
