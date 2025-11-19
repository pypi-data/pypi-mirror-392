#!/usr/bin/env python3
"""
Test statistics and describe methods for trajectory pools.
"""

import pytest


class TestDescribeMethodTrajectoryPool:
    """Test describe() method on trajectory pools."""

    @pytest.mark.parametrize("aggregate", [True, False])
    def test_describe_pool(self, trajectory_pool, aggregate, snapshot):
        """Test describe() returns proper DataFrame for trajectory pool."""
        # Get description
        result = trajectory_pool.describe(dropna=True, aggregate=aggregate)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    def test_describe_with_custom_separator(self, trajectory_pool, snapshot):
        """Test describe() with custom separator for column names."""
        # Get description with dot separator
        result = trajectory_pool.describe(dropna=True, separator=".")

        # Snapshot the result
        snapshot.assert_match(result.to_csv())

    def test_describe_aggregate_columns(self, trajectory_pool, snapshot):
        """Test that describe(aggregate=True) returns aggregate statistics."""
        # Get aggregated description
        result = trajectory_pool.describe(dropna=True, aggregate=True)

        snapshot.assert_match(result.to_csv())


class TestSummarizerTrajectoryPool:
    """Test summarizer mixin on trajectory pools."""

    def test_statistics_snapshot(self, trajectory_pool, snapshot):
        """Test statistics property content with snapshot."""
        # Get statistics
        stats = trajectory_pool.statistics

        # Snapshot the statistics dict as string
        snapshot.assert_match(str(stats))

    def test_format_summary_snapshot(self, trajectory_pool, snapshot):
        """Test format_summary() output with snapshot."""
        # Get formatted summary
        summary = trajectory_pool.format_summary()

        # Snapshot the summary
        snapshot.assert_match(summary)

    def test_add_to_static(self, trajectory_pool, snapshot):
        """Test add_to_static parameter adds descriptions to static_data."""
        # Make a copy to avoid modifying fixture
        pool = trajectory_pool.copy()

        # Call describe with add_to_static=True
        pool.describe(dropna=True, add_to_static=True)

        # Snapshot the static_data
        snapshot.assert_match(pool.static_data.to_csv())
