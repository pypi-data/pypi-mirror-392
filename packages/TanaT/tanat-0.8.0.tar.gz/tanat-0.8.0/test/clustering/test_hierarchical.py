#!/usr/bin/env python3
"""Test Hierarchical clusterer."""

import pytest

from tanat.clustering import HierarchicalClusterer, HierarchicalClustererSettings


class TestHierarchicalClustering:
    """
    Test Hierarchical clustering with different sequence pools and different metrics.
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
    def test_hierarchical(self, sequence_pools, pool_type, metric_str, snapshot):
        """
        Ensure Hierarchical yields the right number of clusters and an additional column in the static features.
        Snapshot is used to check the results of the clustering.
        """
        pool = sequence_pools[pool_type].copy()
        nbc = 5
        hierarchical_settings = HierarchicalClustererSettings(
            metric=metric_str, n_clusters=nbc
        )
        hierarchical = HierarchicalClusterer(settings=hierarchical_settings)
        hierarchical.fit(pool)

        # Check number of clusters
        assert len(hierarchical.clusters) == nbc
        # Check the add of a new column
        assert "__HCLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__HCLUSTERS__"])

    def test_model_caching(self):
        """
        Verify that the model property is cached and returns the same instance.
        """
        hierarchical_settings = HierarchicalClustererSettings(
            metric="edit", n_clusters=3
        )
        hierarchical = HierarchicalClusterer(settings=hierarchical_settings)

        # Access model twice - should be the same instance due to caching
        model1 = hierarchical.model
        model2 = hierarchical.model
        assert model1 is model2

    def test_fitted_model_lifecycle(self, sequence_pools):
        """
        Verify fitted_model lifecycle: None before fit, exists after fit, cleared on cache clear.
        """
        pool = sequence_pools["event"].copy()
        hierarchical_settings = HierarchicalClustererSettings(
            metric="edit", n_clusters=3
        )
        hierarchical = HierarchicalClusterer(settings=hierarchical_settings)

        # Before fit: None
        assert hierarchical.fitted_model is None

        # After fit: exists
        hierarchical.fit(pool)
        assert hierarchical.fitted_model is not None

        # After clear_cache: None again
        hierarchical.clear_cache()
        assert hierarchical.fitted_model is None

    def test_update_settings_clears_cache(self, sequence_pools):
        """
        Verify that update_settings() clears fitted_model when settings change.
        """
        pool = sequence_pools["event"].copy()

        # Test 1: Update via kwargs
        hierarchical = HierarchicalClusterer(
            settings=HierarchicalClustererSettings(metric="edit", n_clusters=3)
        )
        hierarchical.fit(pool)
        assert hierarchical.fitted_model is not None

        hierarchical.update_settings(n_clusters=5)
        assert hierarchical.fitted_model is None
        assert hierarchical.model.n_clusters == 5

    def test_hierarchical_on_trajectory_pool(self, trajectory_pool, snapshot):
        """
        Ensure Hierarchical works on trajectory pools.
        Snapshot is used to check the results of the clustering.
        """
        pool = trajectory_pool.copy()
        nbc = 4
        hierarchical_settings = HierarchicalClustererSettings(
            metric="aggregation",
            n_clusters=nbc,
        )
        hierarchical = HierarchicalClusterer(settings=hierarchical_settings)
        hierarchical.fit(pool)

        # Check number of clusters
        assert len(hierarchical.clusters) == nbc
        # Check the add of a new column
        assert "__HCLUSTERS__" in pool.static_data.columns

        # Verification via snapshot for both normalized results
        snapshot.assert_match(pool.static_data["__HCLUSTERS__"])
