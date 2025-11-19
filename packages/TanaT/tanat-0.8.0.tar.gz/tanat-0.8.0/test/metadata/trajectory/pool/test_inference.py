#!/usr/bin/env python3
"""
Test automatic metadata inference on TrajectoryPool.
"""

import pytest
import pandas as pd
from tanat.trajectory.pool import TrajectoryPool
from tanat.sequence.base.pool import SequencePool
from tanat.metadata.exception import TemporalIncoherenceError


@pytest.fixture
def incompatible_sequence_pool():
    """
    Sequence pools with incompatible temporal metadata for testing inference errors.
    Incompatibility due to TIMESTEP which is different from DATETIME.
    """
    sequence_data = pd.DataFrame(
        {
            "patient_id": [1, 1, 1, 1, 2, 2, 2, 2],
            "timestep": [1, 3, 5, 8, 2, 4, 6, 9],
            "event_type": [
                "admission",
                "diagnosis",
                "treatment",
                "discharge",
                "admission",
                "diagnosis",
                "treatment",
                "discharge",
            ],
        }
    )

    # Create two sequence pools with different timezones
    incompatible_seqpool_event = SequencePool.init(
        "event",
        sequence_data=sequence_data,
        settings={
            "id_column": "patient_id",
            "time_column": "timestep",
            "entity_features": ["event_type"],
        },
        metadata=None,
    )
    return incompatible_seqpool_event


class TestTrajectoryPoolInference:
    """Test metadata inference on trajectory pools."""

    def test_complete_trajectory_metadata_inference(self, sequence_pools, snapshot):
        """
        Test that trajectory infers metadata while using __init__.
        """
        # Create trajectory from sequence pools
        trajectory = TrajectoryPool(
            sequence_pools={
                "event": sequence_pools["event"],
                "state": sequence_pools["state"],
                "interval": sequence_pools["interval"],
            }
        )

        # Snapshot trajectory metadata
        snapshot.assert_match(trajectory.metadata)

    def test_pre_built_trajectory_metadata_inference(self, trajectory_pool, snapshot):
        """
        Test complete trajectory metadata inference.
        Uses pre-built trajectory_pool fixture with all components.
        Note: prebuilt trajectory uses `add_sequence_pool` to build from sequence pools.
        """
        # Snapshot complete metadata structure
        snapshot.assert_match(trajectory_pool.metadata)

    def test_incompatible_sequence_added(
        self, trajectory_pool, incompatible_sequence_pool
    ):
        """
        Test that incompatible sequence pools raise a TemporalIncoherenceError.
        """
        trajectory_pool = trajectory_pool.copy()
        with pytest.raises(TemporalIncoherenceError):
            trajectory_pool.add_sequence_pool(
                incompatible_sequence_pool, "incompatible_event"
            )
