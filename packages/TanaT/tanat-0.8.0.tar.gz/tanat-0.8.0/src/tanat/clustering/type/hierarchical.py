#!/usr/bin/env python3
"""
Hierarchical clusterer.
"""

import logging
from typing import Union, Optional

from sklearn.cluster import AgglomerativeClustering
from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.fallback.typing import Dict
from pypassist.mixin.cachable import Cachable

from ...metric.sequence.base.metric import SequenceMetric
from ...metric.trajectory.base.metric import TrajectoryMetric
from ..clusterer import Clusterer


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class HierarchicalClustererSettings:
    """
    Configuration settings for the HierarchicalClusterer.

    Attributes:
        metric (Union[SequenceMetric, TrajectoryMetric, str]):
            The metric used for clustering. If a string identifier is is provided,
            (e.g., from a YAML configuration), it will be resolved into an `SequenceMetric`
            or `TrajectoryMetric` object from the global configuration.
        n_clusters (int):
            The number of clusters to form. Defaults to 2.
        distance_threshold (float):
            The distance threshold for clustering. If `n_clusters` is None, clustering stops
            when this threshold is reached. Defaults to None.
            If specified, `n_clusters` is ignored.
        linkage (str):
            Linkage criterion for the clustering algorithm. Options include 'complete',
            'average', etc. Defaults to 'complete'.
        model_kwargs (dict):
            Additional keyword arguments for the `AgglomerativeClustering` scikit-learn model.
            Defaults to an empty dictionary.
        cluster_column (str): The column name used to store the clustering results
            as a static feature. Defaults to "__HCLUSTERS__".
    """

    metric: Union[SequenceMetric, TrajectoryMetric, str] = "linearpairwise"
    n_clusters: int = 2
    distance_threshold: Optional[float] = None
    linkage: str = "complete"
    model_kwargs: Dict = Field(default_factory=dict)
    cluster_column: str = "__HCLUSTERS__"


class HierarchicalClusterer(Clusterer, register_name="hierarchical"):
    """
    Hierarchical clustering implementation using AgglomerativeClustering.
    """

    SETTINGS_DATACLASS = HierarchicalClustererSettings

    def __init__(self, settings=None, *, workenv=None):
        """
        Initialize the hierarchical clusterer with the given settings.

        Args:
            settings: Configuration settings for the hierarchical clusterer.
            If None, default HierarchicalClustererSettings will be used.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        if settings is None:
            settings = HierarchicalClustererSettings()

        super().__init__(settings, workenv=workenv)
        self._fitted_model = None

    @Cachable.caching_property
    def model(self):
        """
        Returns an instance of AgglomerativeClustering configured with precomputed metrics
        and the current settings.

        Returns:
            AgglomerativeClustering: The configured classifier.
        """
        forbidden_kwargs = ["metric", "n_clusters", "linkage", "distance_threshold"]
        for kwarg in forbidden_kwargs:
            if kwarg in self.settings.model_kwargs:
                LOGGER.warning(
                    "Invalid argument `%s` provided in model_kwargs. It will be ignored.",
                    kwarg,
                )
                self.settings.model_kwargs.pop(kwarg)

        if self.settings.distance_threshold is not None:
            n_clusters = None
        else:
            n_clusters = self.settings.n_clusters

        return AgglomerativeClustering(
            metric="precomputed",
            n_clusters=n_clusters,
            linkage=self.settings.linkage,
            distance_threshold=self.settings.distance_threshold,
            **self.settings.model_kwargs,
        )

    @Cachable.caching_method()
    def _compute_fit(self, metric, pool):
        """
        Computes and applies the clustering model to the data.

        Args:
            metric: The metric to compute distances between data points.
            pool: The data pool (sequence or trajectory data).
        """
        dist_matrix = metric.collect_as_matrix(pool)
        self._fitted_model = self.model.fit(dist_matrix)
        item_ids = list(dist_matrix.columns)
        self._create_clusters(self._fitted_model.labels_, item_ids)

    @property
    def fitted_model(self):
        """
        Returns the fitted AgglomerativeClustering model.

        Returns:
            AgglomerativeClustering: The fitted model, or None if fit() hasn't been called.
        """
        return self._fitted_model

    def clear_cache(self):
        """
        Clear the cache and reset the fitted model.

        The fitted model is stored separately from cached properties and needs
        to be explicitly reset when the cache is cleared to ensure consistency
        with the clusterer state.
        """
        super().clear_cache()
        self._fitted_model = None

    def _extract_item_ids(self, metric_data):
        """
        Extracts unique item IDs from the metric data.

        Args:
            metric_data (pd.DataFrame): The data containing the metric results.

        Returns:
            List[str]: A list of unique item IDs.
        """
        return list(metric_data.columns)
