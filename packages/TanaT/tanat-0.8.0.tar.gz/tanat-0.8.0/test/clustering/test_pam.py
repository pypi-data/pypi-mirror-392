#!/usr/bin/env python3
"""Test PAM clusterer."""

import pytest

from tanat.clustering import PAMClusterer, PAMClustererSettings


class TestPAMClustering:
    """
    Test PAM clustering with different sequence pools and different metrics.
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
    def test_pam(self, sequence_pools, pool_type, metric_str, snapshot):
        """
        Ensure PAM yields the right number of medoids and an additional columns in the static features.
        Snapshot is used to check the results of the clustering.
        """
        pool = sequence_pools[pool_type].copy()
        nbc = 5
        pam_settings = PAMClustererSettings(metric=metric_str, n_clusters=nbc)
        pam = PAMClusterer(settings=pam_settings)
        pam.fit(pool)

        # Check number of medoids
        assert len(pam.medoids) == nbc
        # Check the add of a new column
        assert "__PAM_CLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__PAM_CLUSTERS__"])

    def test_pam_on_trajectory_pool(self, trajectory_pool, snapshot):
        """
        Ensure PAM works on trajectory pools.
        Snapshot is used to check the results of the clustering.
        """
        pool = trajectory_pool.copy()
        nbc = 4
        pam_settings = PAMClustererSettings(
            metric="aggregation",
            n_clusters=nbc,
        )
        pam = PAMClusterer(settings=pam_settings)
        pam.fit(pool)

        # Check number of medoids
        assert len(pam.medoids) == nbc
        # Check the add of a new column
        assert "__PAM_CLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__PAM_CLUSTERS__"])
