#!/usr/bin/env python3
"""
Test statistics and describe methods for single sequences.
"""

import pytest


class TestDescribeMethod:
    """Test describe() method on single sequences."""

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_single_sequence(self, sequence_pools, seq_type, snapshot):
        """Test describe() returns proper DataFrame for single sequence."""
        # Get first sequence from pool
        pool = sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get description
        result = sequence.describe(aggregate=False, dropna=True)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_with_aggregate(self, sequence_pools, seq_type, snapshot):
        """Test describe() with aggregate=True (should still work for single sequence)."""
        # Get first sequence from pool
        pool = sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get description with aggregate
        result = sequence.describe(aggregate=True, dropna=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_to_static(self, sequence_pools, seq_type, snapshot):
        """Test add_to_static parameter adds descriptions to static_data."""
        # Get first sequence from pool (make a copy to avoid modifying fixture)
        pool = sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id].copy()

        # Call describe with add_to_static=True
        sequence.describe(dropna=True, add_to_static=True)

        # Snapshot the static_data
        snapshot.assert_match(sequence.static_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_single_entity(self, single_entity_sequences, seq_type, snapshot):
        """Test describe() on sequence with single entity."""
        sequence = single_entity_sequences[seq_type]

        # Get description
        result = sequence.describe(aggregate=False, dropna=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_to_static_single_entity(
        self, single_entity_sequences, seq_type, snapshot
    ):
        """Test add_to_static with single entity sequence."""
        # Make a copy to avoid modifying fixture
        sequence = single_entity_sequences[seq_type].copy()

        # Call describe with add_to_static=True
        sequence.describe(dropna=True, add_to_static=True)

        # Snapshot the static_data
        snapshot.assert_match(sequence.static_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_timestep_sequence(
        self, timestep_sequence_pools, seq_type, snapshot
    ):
        """Test describe() with timestep-based sequences (numeric time)."""
        # Get first sequence from pool
        pool = timestep_sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get description
        result = sequence.describe(dropna=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())


class TestSummarizerSequence:
    """Test summarizer mixin on single sequences."""

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_statistics_snapshot(self, sequence_pools, seq_type, snapshot):
        """Test statistics property content with snapshot."""
        # Get first sequence from pool
        pool = sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get statistics
        stats = sequence.statistics

        # Snapshot the statistics dict as string
        snapshot.assert_match(str(stats))

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_format_summary_snapshot(self, sequence_pools, seq_type, snapshot):
        """Test format_summary() output with snapshot."""
        # Get first sequence from pool
        pool = sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get formatted summary
        summary = sequence.format_summary()

        # Snapshot the summary
        snapshot.assert_match(summary)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_statistics_single_entity(
        self, single_entity_sequences, seq_type, snapshot
    ):
        """Test statistics property on sequence with single entity."""
        sequence = single_entity_sequences[seq_type]

        # Get statistics
        stats = sequence.statistics

        # Snapshot the statistics
        snapshot.assert_match(str(stats))

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_format_summary_single_entity(
        self, single_entity_sequences, seq_type, snapshot
    ):
        """Test format_summary() on sequence with single entity."""
        sequence = single_entity_sequences[seq_type]

        # Get formatted summary
        summary = sequence.format_summary()

        # Snapshot the summary
        snapshot.assert_match(summary)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_statistics_timestep_sequence(
        self, timestep_sequence_pools, seq_type, snapshot
    ):
        """Test statistics property with timestep-based sequences."""
        # Get first sequence from pool
        pool = timestep_sequence_pools[seq_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Get statistics
        stats = sequence.statistics

        # Snapshot the statistics
        snapshot.assert_match(str(stats))
