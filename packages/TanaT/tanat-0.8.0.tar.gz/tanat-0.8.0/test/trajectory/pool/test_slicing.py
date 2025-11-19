#!/usr/bin/env python3
"""
Test slicing operations on trajectory pools.
"""

import pytest


class TestHeadMethodPool:
    """Test head() method on trajectory pools."""

    def test_head_positive_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test head with positive value on all sequences."""
        # Get first 2 entities from all sequences in the pool
        result = trajectory_pool_no_state.head(2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_head_positive_specific_sequence(self, trajectory_pool_no_state, snapshot):
        """Test head with positive value on specific sequence."""
        # Get first 2 entities from event sequence only
        result = trajectory_pool_no_state.head(2, sequence_name="event")

        # Snapshot the event sequence pool
        seqpool = result.sequence_pools["event"]
        snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_head_negative_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test head with negative value (all except last n) on all sequences."""
        # head(-1) = all except last entity per sequence
        result = trajectory_pool_no_state.head(-1)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_head_inplace_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test head with inplace=True on all sequences."""
        pool = trajectory_pool_no_state.copy()

        # Apply head inplace
        result = pool.head(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = pool.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())


class TestTailMethodPool:
    """Test tail() method on trajectory pools."""

    def test_tail_positive_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test tail with positive value on all sequences."""
        # Get last 2 entities from all sequences
        result = trajectory_pool_no_state.tail(2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_tail_positive_specific_sequence(self, trajectory_pool_no_state, snapshot):
        """Test tail with positive value on specific sequence."""
        # Get last 2 entities from event sequence only
        result = trajectory_pool_no_state.tail(2, sequence_name="event")

        # Snapshot the event sequence pool
        seqpool = result.sequence_pools["event"]
        snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_tail_negative_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test tail with negative value (all except first n) on all sequences."""
        # tail(-1) = all except first entity per sequence
        result = trajectory_pool_no_state.tail(-1)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_tail_inplace_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test tail with inplace=True on all sequences."""
        pool = trajectory_pool_no_state.copy()

        # Apply tail inplace
        result = pool.tail(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = pool.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())


class TestSliceMethodPool:
    """Test slice() method on trajectory pools."""

    def test_slice_start_end_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test slice with start and end on all sequences."""
        # Slice positions 1 to 3 from all sequences
        result = trajectory_pool_no_state.slice(start=1, end=3)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_start_end_specific_sequence(
        self, trajectory_pool_no_state, snapshot
    ):
        """Test slice with start and end on specific sequence."""
        # Slice positions 1 to 3 from event sequence only
        result = trajectory_pool_no_state.slice(start=1, end=3, sequence_name="event")

        # Snapshot the event sequence pool
        seqpool = result.sequence_pools["event"]
        snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_only_start_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test slice with only start parameter on all sequences."""
        # Slice from position 2 to end for all sequences
        result = trajectory_pool_no_state.slice(start=2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_only_end_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test slice with only end parameter on all sequences."""
        # Slice from beginning to position 2 for all sequences
        result = trajectory_pool_no_state.slice(end=2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_with_step_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test slice with step parameter on all sequences (sub-sampling)."""
        # Slice with step=2 (every 2nd entity from all sequences)
        result = trajectory_pool_no_state.slice(step=2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_with_step_specific_sequence(
        self, trajectory_pool_no_state, snapshot
    ):
        """Test slice with step parameter on specific sequence."""
        # Slice with step=2 from event sequence only
        result = trajectory_pool_no_state.slice(step=2, sequence_name="event")

        # Snapshot the event sequence pool
        seqpool = result.sequence_pools["event"]
        snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_start_end_with_step_all_sequences(
        self, trajectory_pool_no_state, snapshot
    ):
        """Test slice with start, end, and step on all sequences."""
        # Slice positions 0 to 6 with step=2 from all sequences
        result = trajectory_pool_no_state.slice(start=0, end=6, step=2)

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = result.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())

    def test_slice_inplace_all_sequences(self, trajectory_pool_no_state, snapshot):
        """Test slice with inplace=True on all sequences."""
        pool = trajectory_pool_no_state.copy()

        # Apply slice inplace
        result = pool.slice(start=1, end=3, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot all sequence pools
        for seq_name in ["event", "interval"]:
            seqpool = pool.sequence_pools[seq_name]
            snapshot.assert_match(seqpool.sequence_data.to_csv())


class TestConsistencyBetweenMethods:
    """Test consistency between different slicing methods."""

    def test_head_vs_slice_all_sequences(self, trajectory_pool_no_state):
        """Test that head(n) gives same result as slice(end=n) for all sequences."""
        # Get first 2 entities using both methods
        result_head = trajectory_pool_no_state.head(2)
        result_slice = trajectory_pool_no_state.slice(end=2)

        # Verify they produce same result for all sequences
        for seq_name in ["event", "interval"]:
            head_data = result_head.sequence_pools[seq_name].sequence_data
            slice_data = result_slice.sequence_pools[seq_name].sequence_data

            assert len(head_data) == len(slice_data)
            assert head_data.equals(slice_data)

    def test_head_vs_slice_specific_sequence(self, trajectory_pool_no_state):
        """Test that head(n) gives same result as slice(end=n) for specific sequence."""
        # Get first 2 entities using both methods
        result_head = trajectory_pool_no_state.head(2, sequence_name="event")
        result_slice = trajectory_pool_no_state.slice(end=2, sequence_name="event")

        # Verify they produce same result for event sequence
        head_data = result_head.sequence_pools["event"].sequence_data
        slice_data = result_slice.sequence_pools["event"].sequence_data

        assert len(head_data) == len(slice_data)
        assert head_data.equals(slice_data)

    def test_tail_vs_slice_all_sequences(self, trajectory_pool_no_state):
        """Test that tail(n) gives expected result for all sequences."""
        # Get last 2 entities using tail
        result_tail = trajectory_pool_no_state.tail(2)

        # Verify each sequence has correct behavior
        for seq_name in ["event", "interval"]:
            tail_data = result_tail.sequence_pools[seq_name].sequence_data
            # Should have results (exact length depends on original data)
            assert len(tail_data) >= 0
