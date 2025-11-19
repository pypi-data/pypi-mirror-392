#!/usr/bin/env python3
"""
Test slicing operations on sequence pools.
"""

import pytest


class TestHeadMethodPool:
    """Test head() method on sequence pools."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_positive(self, sequence_pools, seq_type, snapshot):
        """Test head with positive value on pool (first N entities per sequence)."""
        pool = sequence_pools[seq_type]

        # Get first 2 entities from each sequence
        result = pool.head(2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_negative(self, sequence_pools, seq_type, snapshot):
        """Test head with negative value (all except last n) on pool."""
        pool = sequence_pools[seq_type]

        # head(-1) = all except last entity per sequence
        result = pool.head(-1)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_inplace(self, sequence_pools, seq_type, snapshot):
        """Test head with inplace=True on pool."""
        pool = sequence_pools[seq_type].copy()

        # Apply head inplace
        result = pool.head(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified pool data
        snapshot.assert_match(pool.sequence_data.to_csv())


class TestTailMethodPool:
    """Test tail() method on sequence pools."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_positive(self, sequence_pools, seq_type, snapshot):
        """Test tail with positive value on pool (last N entities per sequence)."""
        pool = sequence_pools[seq_type]

        # Get last 2 entities from each sequence
        result = pool.tail(2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_negative(self, sequence_pools, seq_type, snapshot):
        """Test tail with negative value on pool (all but first N per sequence)."""
        pool = sequence_pools[seq_type]

        # Get all but first entity from each sequence
        result = pool.tail(-1)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_inplace(self, sequence_pools, seq_type, snapshot):
        """Test tail with inplace=True on pool."""
        pool = sequence_pools[seq_type].copy()

        # Apply tail inplace
        result = pool.tail(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified pool data
        snapshot.assert_match(pool.sequence_data.to_csv())


class TestSliceMethodPool:
    """Test slice() method on sequence pools."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_start_end(self, sequence_pools, seq_type, snapshot):
        """Test slice with start and end on pool."""
        pool = sequence_pools[seq_type]

        # Slice positions 1 to 3 from each sequence
        result = pool.slice(start=1, end=3)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_start(self, sequence_pools, seq_type, snapshot):
        """Test slice with only start parameter on pool."""
        pool = sequence_pools[seq_type]

        # Slice from position 2 to end for each sequence
        result = pool.slice(start=2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_end(self, sequence_pools, seq_type, snapshot):
        """Test slice with only end parameter on pool."""
        pool = sequence_pools[seq_type]

        # Slice from beginning to position 2 for each sequence
        result = pool.slice(end=2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_inplace(self, sequence_pools, seq_type, snapshot):
        """Test slice with inplace=True on pool."""
        pool = sequence_pools[seq_type].copy()

        # Apply slice inplace
        result = pool.slice(start=1, end=3, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified pool data
        snapshot.assert_match(pool.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_with_step(self, sequence_pools, seq_type, snapshot):
        """Test slice with step parameter on pool (sub-sampling)."""
        pool = sequence_pools[seq_type]

        # Slice with step=2 (every 2nd entity from each sequence)
        result = pool.slice(step=2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_start_end_with_step(self, sequence_pools, seq_type, snapshot):
        """Test slice with start, end, and step on pool."""
        pool = sequence_pools[seq_type]

        # Slice positions 0 to 6 with step=2 from each sequence
        result = pool.slice(start=0, end=6, step=2)

        # Snapshot the pool data
        snapshot.assert_match(result.sequence_data.to_csv())


class TestConsistencyBetweenMethods:
    """Test consistency between different slicing methods."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_vs_slice(self, sequence_pools, seq_type):
        """Test that head(n) gives same result as slice(end=n)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get first 2 entities using both methods
        result_head = sequence.head(2)
        result_slice = sequence.slice(end=2)

        # Verify they produce same result
        assert len(result_head) == len(result_slice)
        assert result_head.sequence_data.equals(result_slice.sequence_data)

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_vs_slice(self, sequence_pools, seq_type):
        """Test that tail(n) gives same result as slice(start=-n)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]
        seq_length = len(sequence)

        # Get last 2 entities using both methods
        result_tail = sequence.tail(2)
        result_slice = sequence.slice(start=seq_length - 2)

        # Verify they produce same result
        assert len(result_tail) == len(result_slice)
        assert result_tail.sequence_data.equals(result_slice.sequence_data)

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_getitem_vs_slice_method(self, sequence_pools, seq_type):
        """Test that sequence[1:3] gives same result as sequence.slice(1, 3)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice using both methods
        result_getitem = sequence[1:3]
        result_slice = sequence.slice(start=1, end=3)

        # Verify they produce same result
        assert len(result_getitem) == len(result_slice)
        assert result_getitem.sequence_data.equals(result_slice.sequence_data)
