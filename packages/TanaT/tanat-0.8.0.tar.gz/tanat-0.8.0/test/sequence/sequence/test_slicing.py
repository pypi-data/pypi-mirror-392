#!/usr/bin/env python3
"""
Test slicing operations on individual sequences.
"""

import pytest


class TestGetItemSingleIndex:
    """Test __getitem__ with single index access."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_first_entity(self, sequence_pools, seq_type, snapshot):
        """Test accessing first entity with index 0."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get first entity
        entity = sequence[0]

        # Snapshot the entity data
        assert entity == snapshot

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_last_entity(self, sequence_pools, seq_type, snapshot):
        """Test accessing last entity with index -1."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get last entity
        entity = sequence[-1]

        # Snapshot the entity data
        assert entity == snapshot

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_middle_entity(self, sequence_pools, seq_type, snapshot):
        """Test accessing middle entity with positive index."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get second entity (index 1)
        entity = sequence[1]

        # Snapshot the entity data
        assert entity == snapshot

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_negative_index(self, sequence_pools, seq_type, snapshot):
        """Test accessing entity with negative index -2."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get second to last entity
        entity = sequence[-2]

        # Snapshot the entity data
        assert entity == snapshot


class TestGetItemSlice:
    """Test __getitem__ with slice notation."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_start_end(self, sequence_pools, seq_type, snapshot):
        """Test slicing with start and end indices."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from index 1 to 3 (exclusive)
        sliced = sequence[1:3]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_start(self, sequence_pools, seq_type, snapshot):
        """Test slicing with only start index."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from index 2 to end
        sliced = sequence[2:]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_end(self, sequence_pools, seq_type, snapshot):
        """Test slicing with only end index."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from beginning to index 2 (exclusive)
        sliced = sequence[:2]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_negative_end(self, sequence_pools, seq_type, snapshot):
        """Test slicing with negative end index (all but last)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice all but last entity
        sliced = sequence[:-1]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_both_negative(self, sequence_pools, seq_type, snapshot):
        """Test slicing with both negative indices (without first and last)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice without first and last entity
        sliced = sequence[1:-1]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_negative_start(self, sequence_pools, seq_type, snapshot):
        """Test slicing with negative start index (last N entities)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get last 2 entities
        sliced = sequence[-2:]

        # Snapshot the sequence data
        snapshot.assert_match(sliced.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_with_step(self, sequence_pools, seq_type, snapshot):
        """Test slicing with step parameter (sub-sampling)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice with step=2 (every 2nd element)
        result = sequence[::2]

        # Snapshot the result
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_step_negative_not_supported(self, sequence_pools, seq_type):
        """Test that negative step is not supported (temporal sequences)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Negative step should raise validation error
        with pytest.raises(TypeError):
            _ = sequence[::-1]

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_step_zero_not_supported(self, sequence_pools, seq_type):
        """Test that step=0 is not supported."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # step=0 should raise validation error
        with pytest.raises(TypeError):
            _ = sequence[::0]


class TestHeadMethod:
    """Test head() method for getting first N entities."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_positive(self, sequence_pools, seq_type, snapshot):
        """Test head with positive value (first N entities)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get first 2 entities
        result = sequence.head(2)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_negative(self, sequence_pools, seq_type, snapshot):
        """Test head with negative value (all except last n)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # head(-2) = all except last 2
        result = sequence.head(-2)

        # Snapshot the result
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_one(self, sequence_pools, seq_type, snapshot):
        """Test head with value 1 (single entity)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get first entity
        result = sequence.head(1)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_zero(self, sequence_pools, seq_type):
        """Test head with value 0 raises TypeError."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # head(0) should raise error (validation error becomes TypeError)
        with pytest.raises(TypeError):
            sequence.head(0)

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_head_inplace(self, sequence_pools, seq_type, snapshot):
        """Test head with inplace=True modifies sequence."""
        pool = sequence_pools[seq_type]
        sequence = pool[1].copy()

        # Apply head inplace
        result = sequence.head(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified sequence data
        snapshot.assert_match(sequence.sequence_data.to_csv())


class TestTailMethod:
    """Test tail() method for getting last N entities."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_positive(self, sequence_pools, seq_type, snapshot):
        """Test tail with positive value (last N entities)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get last 2 entities
        result = sequence.tail(2)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_negative(self, sequence_pools, seq_type, snapshot):
        """Test tail with negative value (all but first N entities)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get all but first 2 entities
        result = sequence.tail(-2)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_one(self, sequence_pools, seq_type, snapshot):
        """Test tail with value 1 (single entity)."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Get a sequence with the last entity
        result = sequence.tail(1)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_zero(self, sequence_pools, seq_type):
        """Test tail with value 0 raises TypeError."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # tail(0) should raise error (validation error becomes TypeError)
        with pytest.raises(TypeError):
            sequence.tail(0)

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_tail_inplace(self, sequence_pools, seq_type, snapshot):
        """Test tail with inplace=True modifies sequence."""
        pool = sequence_pools[seq_type]
        sequence = pool[1].copy()

        # Apply tail inplace
        result = sequence.tail(2, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified sequence data
        snapshot.assert_match(sequence.sequence_data.to_csv())


class TestSliceMethod:
    """Test slice() method for range-based filtering."""

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_start_end(self, sequence_pools, seq_type, snapshot):
        """Test slice with start and end parameters."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from position 1 to 3
        result = sequence.slice(start=1, end=3)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_start(self, sequence_pools, seq_type, snapshot):
        """Test slice with only start parameter."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from position 2 to end
        result = sequence.slice(start=2)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_only_end(self, sequence_pools, seq_type, snapshot):
        """Test slice with only end parameter."""
        pool = sequence_pools[seq_type]
        sequence = pool[1]

        # Slice from beginning to position 2
        result = sequence.slice(end=2)

        # Snapshot the sequence data
        snapshot.assert_match(result.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "interval"])
    def test_slice_inplace(self, sequence_pools, seq_type, snapshot):
        """Test slice with inplace=True modifies sequence."""
        pool = sequence_pools[seq_type]
        sequence = pool[1].copy()

        # Apply slice inplace
        result = sequence.slice(start=1, end=3, inplace=True)

        # Verify returns None
        assert result is None

        # Snapshot the modified sequence data
        snapshot.assert_match(sequence.sequence_data.to_csv())
