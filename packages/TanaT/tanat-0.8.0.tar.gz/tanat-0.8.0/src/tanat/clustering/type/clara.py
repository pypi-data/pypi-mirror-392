#!/usr/bin/env python3
"""
CLARA clusterer.
"""

import logging
from typing import Union, Optional

import numpy as np

from pydantic import Field
from pydantic.dataclasses import dataclass
from pypassist.mixin.cachable import Cachable
from pypassist.dataclass.decorators.viewer import viewer

from ..clusterer import Clusterer
from ..mixin.medoid import MedoidMixin
from .pam import PAMClusterer, PAMClustererSettings
from ...metric.sequence.base.metric import SequenceMetric
from ...metric.trajectory.base.metric import TrajectoryMetric

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class CLARAClustererSettings:
    """
    Configuration settings for the CLARAClusterer.

    Attributes:
        metric (Union[SequenceMetric, TrajectoryMetric, str]):
            The metric used for clustering. If a string identifier is provided,
            (e.g., from a YAML configuration), it will be resolved into an `SequenceMetric`
            or `TrajectoryMetric` object from the global configuration.
        sampling_ratio (float):
            Proportion of the dataset to sample for each PAM instance.
            Must be between 0 (exclusive) and 1 (inclusive). Defaults to 0.1 (10% of data).
        nb_pam_instances (int):
            Number of PAM instances to run on different samples.
            The best result across all instances is kept. Must be greater than 0. Defaults to 5.
        n_clusters (int):
            The number of clusters to form. Must be greater than 0. Defaults to 2.
        max_iter (int):
            Maximum number of iterations for the PAM swap phase.
            Must be greater than 0. Defaults to 50.
        random_state (Optional[int]):
            Random seed for reproducibility. If None, results will vary between runs.
            Defaults to None.
        cluster_column (str):
            The column name used to store the clustering results
            as a static feature. Defaults to "__CLARA_CLUSTERS__".
    """

    metric: Union[SequenceMetric, TrajectoryMetric, str] = "linearpairwise"
    sampling_ratio: float = Field(default=0.1, gt=0, le=1.0)
    nb_pam_instances: int = Field(default=5, gt=0)
    n_clusters: int = Field(default=2, gt=0)
    max_iter: int = Field(default=50, gt=0)
    random_state: Optional[int] = None
    cluster_column: str = "__CLARA_CLUSTERS__"


class CLARAClusterer(MedoidMixin, Clusterer, register_name="clara"):
    """
    CLARA is a clustering algorithm derived from PAM for large datasets.
    The basic idea behind CLARA is to draw several samples from the dataset and apply
    the K-Medoids (PAM) algorithm to each sample. The objective is to find the best set
    of medoids that minimize the clustering cost. By applying clustering on multiple
    smaller samples, CLARA identifies a set of medoids that perform well for the entire
    dataset.

    .. important::
        The clustering technique is sound with metrics that hold distance's properties.
        More specifically, the triangular inegality must hold to ensure the convergence
        of the algorithm.

    .. note::
        Contrary to PAM which requires to precompute the distance matrix. CLARA precomputes
        several distance matrices on several small samples of the data.
        This lower significantly the memory consumption.

    Example:

        Clustering with CLARA, with 5 clusters and a linear pairwise metric.

        >>> cluster_settings = CLARAClustererSettings(metric="linearpairwise", n_clusters=5)
        >>> clusterer = CLARAClusterer(settings=cluster_settings)
        >>> clusterer.fit(pool)


    .. seealso::

        :py:class:`PAMClusterer`
            PAM (Partition Around Medoids) is the base clusterer for CLARA.
    """

    SETTINGS_DATACLASS = CLARAClustererSettings

    def __init__(self, settings=None, *, workenv=None):
        """
        Initialize the CLARA clusterer with the given settings.

        Args:
            settings: Configuration settings for the CLARA clusterer.
                If None, default CLARAClustererSettings will be used.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        if settings is None:
            settings = CLARAClustererSettings()

        Clusterer.__init__(self, settings, workenv=workenv)
        MedoidMixin.__init__(self)

    def _pam_settings(self):
        """
        Return the settings of PAM from the internal settings of CLARA
        """
        return PAMClustererSettings(
            cluster_column=self.settings.cluster_column,
            metric=self.settings.metric,
            n_clusters=self.settings.n_clusters,
            max_iter=self.settings.max_iter,
        )

    @Cachable.caching_method()
    def _compute_fit(self, metric, pool):
        optimal_medoids = None
        optimal_inertia = float("inf")

        labels = None

        # Set random seed for reproducibility only if specified
        if self.settings.random_state is not None:
            rng = np.random.default_rng(self.settings.random_state)
        else:
            rng = np.random.default_rng()  # Uses default (time-based) seed

        for _ in range(self.settings.nb_pam_instances):
            # sample the pool
            sample_size = int(self.settings.sampling_ratio * len(pool))
            # Sort IDs to ensure deterministic ordering across runs
            sorted_ids = sorted(pool.unique_ids)
            sampled_ids = rng.choice(sorted_ids, size=sample_size, replace=False)
            subpool = pool.subset(sampled_ids.tolist())

            # execute PAM on this subpool
            clusterer = PAMClusterer(
                settings=self._pam_settings(), workenv=self._workenv
            )
            clusterer.fit(subpool)

            # -- evaluate the result on the complete list of examples
            # compute all distances in a comprehensive way
            item_idx = sorted_ids  # Use sorted IDs for consistent ordering
            dists = np.array(
                [
                    [metric(pool[obj], pool[m]) for m in clusterer.medoids]
                    for obj in item_idx
                ]
            )
            # evaluate the inertia
            inertia = np.sum(np.min(dists, axis=1))

            if inertia < optimal_inertia:
                # save the results for this instance
                optimal_medoids = clusterer.medoids
                optimal_inertia = inertia
                # labels
                labels = np.argmin(dists, axis=1)
        # create clusters based on the optimal PAM instance
        self._medoids = optimal_medoids
        self._create_clusters(labels, item_idx)
