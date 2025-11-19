#!/usr/bin/env python3
"""
Test initialization of trajectory pool.
"""

import pytest

from pydantic import ValidationError

from tanat.trajectory.pool import TrajectoryPool
from tanat.trajectory.settings.pool import TrajectoryPoolSettings


class TestInitTrajectoryPool:
    """
    Tests for TrajectoryPool initialization and sequence pool addition.
    """

    def test_initialize_settings(self):
        """
        Test that TrajectoryPoolSettings can be initialized correctly.
        """
        settings = TrajectoryPoolSettings(
            id_column="patient_id",
            intersection=False,
            static_features=["gender", "age"],
        )
        assert isinstance(settings, TrajectoryPoolSettings)

    def test_conflict_detected_in_settings(self):
        """
        Test that conflicting column names in TrajectoryPoolSettings raise an error.
        """
        with pytest.raises(ValidationError):
            TrajectoryPoolSettings(
                id_column="patient_id",
                intersection=False,
                static_features=["patient_id"],
            )

    def test_static_features_single_string_conversion(self):
        """
        Test that a single string for static_features is automatically converted to a list.

        This verifies user-friendly behavior: users can pass a simple string when they
        have only one static feature, instead of requiring a list.
        """

        static_feature_str = "age"
        settings = TrajectoryPoolSettings(
            id_column="patient_id",
            intersection=False,
            static_features=static_feature_str,
        )

        # Verify it was converted to a list
        assert isinstance(settings.static_features, list)
        assert len(settings.static_features) == 1
        assert settings.static_features[0] == static_feature_str

    def test_initialize_empty_pool(self):
        """
        Test that `init_empty()` creates a TrajectoryPool with no sequence pools.
        """
        traj_pool = TrajectoryPool.init_empty()

        assert isinstance(traj_pool, TrajectoryPool)
        assert traj_pool.sequence_pools == {}

    def test_add_multiple_sequence_pools(self, sequence_pools):
        """
        Test that sequence pools can be added in a chained fashion using `add_sequence_pool()`.
        """
        traj_pool = TrajectoryPool.init_empty()

        traj_pool.add_sequence_pool(sequence_pools["event"], "event").add_sequence_pool(
            sequence_pools["interval"], "interval"
        ).add_sequence_pool(sequence_pools["state"], "state")

        assert isinstance(traj_pool, TrajectoryPool)
        assert sorted(list(traj_pool.sequence_pools.keys())) == [
            "event",
            "interval",
            "state",
        ]
