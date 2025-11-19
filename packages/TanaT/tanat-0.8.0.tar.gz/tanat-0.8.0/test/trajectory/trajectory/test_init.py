#!/usr/bin/env python3
"""
Test initialization of trajectory.
"""

import pytest

from pydantic import ValidationError

from tanat.trajectory.trajectory import Trajectory
from tanat.trajectory.settings.trajectory import TrajectorySettings


class TestInitTrajectory:
    """
    Tests for Trajectory initialization.
    """

    def test_initialize_settings(self):
        """
        Test that TrajectorySettings can be initialized correctly.
        """
        settings = TrajectorySettings(
            id_column="patient_id",
            static_features=["gender", "age"],
        )
        assert isinstance(settings, TrajectorySettings)

    def test_conflict_detected_in_settings(self):
        """
        Test that conflicting column names in TrajectorySettings raise an error.
        """
        with pytest.raises(ValidationError):
            TrajectorySettings(
                id_column="patient_id",
                static_features=["patient_id"],
            )

    def test_static_features_single_string_conversion(self):
        """
        Test that a single string for static_features is automatically converted to a list.

        This verifies user-friendly behavior: users can pass a simple string when they
        have only one static feature, instead of requiring a list.
        """

        static_feature_str = "age"
        settings = TrajectorySettings(
            id_column="patient_id",
            static_features=static_feature_str,
        )

        # Verify it was converted to a list
        assert isinstance(settings.static_features, list)
        assert len(settings.static_features) == 1
        assert settings.static_features[0] == static_feature_str

    def test_initialize_trajectory(self, sequence_pools):
        """
        Test trajectory initialization.
        """
        traj = Trajectory(id_value=3, sequence_pools=sequence_pools)
        assert sorted(list(traj.sequences.keys())) == ["event", "interval", "state"]
