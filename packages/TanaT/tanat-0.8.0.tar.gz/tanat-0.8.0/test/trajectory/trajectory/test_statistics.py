#!/usr/bin/env python3
"""
Test statistics and describe methods for single trajectories.
"""


class TestDescribeMethodTrajectory:
    """Test describe() method on single trajectories."""

    def test_describe_single_trajectory(self, trajectory_pool, snapshot):
        """Test describe() returns proper DataFrame for single trajectory."""
        # Get first trajectory from pool
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id]

        # Get description (with dropna=True since test data may have NaT)
        result = trajectory.describe(dropna=True, aggregate=False)

        # Snapshot the result as CSV
        snapshot.assert_match(result.to_csv())

    def test_describe_with_custom_separator(self, trajectory_pool, snapshot):
        """Test describe() with custom separator for column names."""
        # Get first trajectory
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id]

        # Get description with dot separator
        result = trajectory.describe(dropna=True, separator=".")

        # Snapshot the result
        snapshot.assert_match(result.to_csv())

    def test_describe_with_aggregate(self, trajectory_pool, snapshot):
        """Test describe() with aggregate=True (aggregates across sequences)."""
        # Get first trajectory
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id]

        # Get aggregated description
        result = trajectory.describe(dropna=True, aggregate=True)

        # Snapshot the result
        snapshot.assert_match(result.to_csv())


class TestSummarizerTrajectory:
    """Test summarizer mixin on single trajectories."""

    def test_statistics_snapshot(self, trajectory_pool, snapshot):
        """Test statistics property content with snapshot."""
        # Get first trajectory
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id]

        # Get statistics
        stats = trajectory.statistics

        # Snapshot the statistics dict as string
        snapshot.assert_match(str(stats))

    def test_format_summary_snapshot(self, trajectory_pool, snapshot):
        """Test format_summary() output with snapshot."""
        # Get first trajectory
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id]

        # Get formatted summary
        summary = trajectory.format_summary()

        # Snapshot the summary
        snapshot.assert_match(summary)

    def test_add_to_static(self, trajectory_pool, snapshot):
        """Test add_to_static parameter adds descriptions to static_data."""
        # Get first trajectory and make a copy to avoid modifying fixture
        trajectory_id = list(trajectory_pool.unique_ids)[0]
        trajectory = trajectory_pool[trajectory_id].copy()

        # Call describe with add_to_static=True
        trajectory.describe(dropna=True, add_to_static=True)

        # Snapshot the static_data
        snapshot.assert_match(trajectory.static_data.to_csv())
