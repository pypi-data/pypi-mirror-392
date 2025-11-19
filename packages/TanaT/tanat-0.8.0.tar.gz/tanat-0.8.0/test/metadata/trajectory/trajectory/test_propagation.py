#!/usr/bin/env python3
"""
Test metadata propagation from single Trajectory to its sequence.
"""

import pytest


@pytest.fixture
def single_trajectory(trajectory_pool, single_id_data):
    """Create a single trajectory with specific patient ID."""
    # Get the patient ID from single_id_data
    patient_id = single_id_data["static_data"]["patient_id"].iloc[0]

    # Extract single trajectory from pool
    return trajectory_pool[patient_id]


class TestSingleTrajectoryPropagation:
    """Test that updates propagate consistently within a single trajectory."""

    def test_timezone_propagates_to_all_sequences(self, single_trajectory, snapshot):
        """
        Test timezone propagation to all sequences within trajectory.
        """
        single_trajectory = single_trajectory.copy()
        single_trajectory.update_temporal_metadata(timezone="Europe/London")

        # Multiple snapshots: verify trajectory + each sequence consistency
        snapshot.assert_match(single_trajectory.metadata)
        snapshot.assert_match(single_trajectory.sequences["event"].metadata)
        snapshot.assert_match(single_trajectory.sequences["state"].metadata)
        snapshot.assert_match(single_trajectory.sequences["interval"].metadata)

    def test_format_propagates_to_all_sequences(self, single_trajectory, snapshot):
        """
        Test format propagation to all sequences within trajectory.
        """
        single_trajectory = single_trajectory.copy()
        single_trajectory.update_temporal_metadata(format="%d-%m-%Y")
        # Verify consistency across all sequences in this trajectory
        snapshot.assert_match(single_trajectory.metadata)
        snapshot.assert_match(single_trajectory.sequences["event"].metadata)
        snapshot.assert_match(single_trajectory.sequences["state"].metadata)
        snapshot.assert_match(single_trajectory.sequences["interval"].metadata)

    def test_granularity_propagates_to_all_sequences(self, single_trajectory, snapshot):
        """
        Test granularity propagation to all sequences within trajectory.
        """
        single_trajectory = single_trajectory.copy()
        single_trajectory.update_temporal_metadata(granularity="HOUR")
        # Verify consistency
        snapshot.assert_match(single_trajectory.metadata)
        snapshot.assert_match(single_trajectory.sequences["event"].metadata)
        snapshot.assert_match(single_trajectory.sequences["state"].metadata)
        snapshot.assert_match(single_trajectory.sequences["interval"].metadata)

    def test_chained_updates_maintain_consistency(self, single_trajectory, snapshot):
        """
        Test that chained updates (temporal + static) maintain consistency within trajectory.
        """
        single_trajectory = single_trajectory.copy()

        # Chain temporal and static updates on this trajectory
        single_trajectory.update_temporal_metadata(
            timezone="America/Chicago"
        ).update_temporal_metadata(format="%m/%d/%Y").update_static_metadata(
            feature_name="gender",
            data_type="categorical",
            categories=["M", "F", "Other"],
        )
        # Snapshot consistency within this trajectory
        snapshot.assert_match(single_trajectory.metadata)
        snapshot.assert_match(single_trajectory.sequences["event"].metadata)
        snapshot.assert_match(single_trajectory.sequences["state"].metadata)
        snapshot.assert_match(single_trajectory.sequences["interval"].metadata)
