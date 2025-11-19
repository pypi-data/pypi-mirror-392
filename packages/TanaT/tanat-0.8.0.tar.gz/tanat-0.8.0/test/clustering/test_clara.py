#!/usr/bin/env python3
"""Test CLARA clusterer."""


import pytest

from tanat.clustering import CLARAClusterer, CLARAClustererSettings


class TestCLARAClustering:
    """
    Test CLARA clustering with different sequence pools and different metrics.
    """

    @pytest.mark.parametrize(
        "pool_type, metric_str",
        [
            ("event", "edit"),
            ("state", "edit"),
            ("interval", "edit"),
            ("event", "lcp"),
            ("state", "lcp"),
            ("interval", "lcp"),
        ],
    )
    def test_clara(self, sequence_pools, pool_type, metric_str, snapshot):
        """
        Ensure CLARA yields the right number of medoids and an additional columns in the static features.
        Snapshot is used to check the results of the clustering.
        """
        pool = sequence_pools[pool_type].copy()
        nbc = 5
        clara_settings = CLARAClustererSettings(
            metric=metric_str,
            n_clusters=nbc,
            sampling_ratio=0.5,
            nb_pam_instances=3,
            random_state=42,  # For reproducibility
        )
        clara = CLARAClusterer(settings=clara_settings)
        clara.fit(pool)

        # Check number of medoids
        assert len(clara.medoids) == nbc
        # Check the add of a new column
        assert "__CLARA_CLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__CLARA_CLUSTERS__"])

    def test_clara_on_trajectory_pool(self, trajectory_pool, snapshot):
        """
        Ensure CLARA works on trajectory pools.
        Snapshot is used to check the results of the clustering.
        """
        pool = trajectory_pool.copy()
        nbc = 4
        clara_settings = CLARAClustererSettings(
            metric="aggregation",
            n_clusters=nbc,
            sampling_ratio=0.5,
            nb_pam_instances=3,
            random_state=42,  # For reproducibility
        )
        clara = CLARAClusterer(settings=clara_settings)
        clara.fit(pool)

        # Check number of medoids
        assert len(clara.medoids) == nbc
        # Check the add of a new column
        assert "__CLARA_CLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__CLARA_CLUSTERS__"])
