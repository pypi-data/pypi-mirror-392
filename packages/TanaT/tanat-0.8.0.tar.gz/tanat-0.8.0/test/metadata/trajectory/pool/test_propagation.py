#!/usr/bin/env python3
"""
Test metadata propagation from TrajectoryPool to sequence pools.
"""

import pytest


class TestTrajectoryPoolPropagation:
    """Test that updates propagate consistently across all sequence pools."""

    def test_inital_propagation_to_all_sequences(self, trajectory_pool, snapshot):
        """
        Test initial metadata propagation to ALL sequence pools.
        Verifies that trajectory → sequence propagation maintains consistency.
        """
        trajectory_pool = trajectory_pool.copy()

        # Snapshot trajectory and each sequence metadata
        snapshot.assert_match(trajectory_pool.metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["event"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["state"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["interval"].metadata)

    def test_update_propagates_to_all_sequences(self, trajectory_pool, snapshot):
        """
        Test timezone propagation to ALL sequence pools.
        Verifies that trajectory → sequence propagation maintains consistency.
        """
        trajectory_pool = trajectory_pool.copy()
        trajectory_pool.update_temporal_metadata(timezone="UTC")

        # Multiple snapshots: verify trajectory + each sequence consistency
        snapshot.assert_match(trajectory_pool.metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["event"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["state"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["interval"].metadata)

    def test_chained_updates_propagate_correctly(self, trajectory_pool, snapshot):
        """
        Test that chained updates propagate correctly.
        """
        trajectory_pool = trajectory_pool.copy()

        # Chain temporal and static updates
        trajectory_pool.update_temporal_metadata(
            timezone="UTC"
        ).update_temporal_metadata(format="%Y-%m-%d").update_static_metadata(
            feature_name="gender",
            data_type="categorical",
            categories=["M", "F", "Other"],
        )

        # Snapshot consistency
        snapshot.assert_match(trajectory_pool.metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["event"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["state"].metadata)
        snapshot.assert_match(trajectory_pool.sequence_pools["interval"].metadata)
