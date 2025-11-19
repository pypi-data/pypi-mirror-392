#!/usr/bin/env python3
"""
Test automatic metadata inference on single Trajectory.
"""

import pytest


@pytest.fixture
def single_trajectory(trajectory_pool, single_id_data):
    """Create a single trajectory with specific patient ID."""
    # Get the patient ID from single_id_data
    patient_id = single_id_data["static_data"]["patient_id"].iloc[0]

    # Extract single trajectory from pool
    return trajectory_pool[patient_id]


class TestSingleTrajectoryInference:
    """Test metadata inference on single trajectory."""

    def test_infer_metadata_single_trajectory(self, single_trajectory, snapshot):
        """
        Test that trajectory infers metadata correctly.
        """
        # Snapshot trajectory metadata
        snapshot.assert_match(single_trajectory.metadata)
