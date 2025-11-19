#!/usr/bin/env python3
"""
Test statistics and describe methods for sequence pools.
"""

import pytest


class TestDescribeMethodPool:
    """Test describe() method on sequence pools."""

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_pool_aggregated(self, sequence_pools, seq_type, snapshot):
        """Test describe() with aggregate=True returns pool-level statistics."""
        pool = sequence_pools[seq_type]

        # Get aggregated description
        result = pool.describe(aggregate=True, dropna=True)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_pool_per_sequence(self, sequence_pools, seq_type, snapshot):
        """Test describe() with aggregate=False returns per-sequence statistics."""
        pool = sequence_pools[seq_type]

        # Get per-sequence description
        result = pool.describe(aggregate=False, dropna=True)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_pool_with_dropna_false(self, sequence_pools, seq_type, snapshot):
        """Test describe() with dropna=False includes all columns."""
        pool = sequence_pools[seq_type]

        # Get description without dropping NAs
        result = pool.describe(aggregate=True, dropna=False)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_timestep_pool(self, timestep_sequence_pools, seq_type, snapshot):
        """Test describe() with timestep-based pools (numeric time)."""
        pool = timestep_sequence_pools[seq_type]

        # Get per-sequence description
        result = pool.describe(aggregate=False, dropna=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_describe_timestep_pool_aggregated(
        self, timestep_sequence_pools, seq_type, snapshot
    ):
        """Test describe() with aggregate=True on timestep pools."""
        pool = timestep_sequence_pools[seq_type]

        # Get aggregated description
        result = pool.describe(aggregate=True, dropna=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())


class TestSummarizerSeqPool:
    """Test summarizer mixin on sequence pools."""

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_statistics_snapshot(self, sequence_pools, seq_type, snapshot):
        """Test statistics property content with snapshot."""
        pool = sequence_pools[seq_type]

        # Get statistics
        stats = pool.statistics

        # Snapshot the statistics dict as string
        snapshot.assert_match(str(stats))

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_format_summary_snapshot(self, sequence_pools, seq_type, snapshot):
        """Test format_summary() output with snapshot."""
        pool = sequence_pools[seq_type]

        # Get formatted summary
        summary = pool.format_summary()

        # Snapshot the summary
        snapshot.assert_match(summary)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_add_to_static(self, sequence_pools, seq_type, snapshot):
        """Test add_to_static parameter adds descriptions to static_data."""
        # Make a copy to avoid modifying fixture
        pool = sequence_pools[seq_type].copy()

        # Call describe with add_to_static=True
        pool.describe(dropna=True, add_to_static=True)

        # Snapshot the static_data
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_statistics_timestep_pool(
        self, timestep_sequence_pools, seq_type, snapshot
    ):
        """Test statistics property with timestep-based pools."""
        pool = timestep_sequence_pools[seq_type]

        # Get statistics
        stats = pool.statistics

        # Snapshot the statistics
        snapshot.assert_match(str(stats))
