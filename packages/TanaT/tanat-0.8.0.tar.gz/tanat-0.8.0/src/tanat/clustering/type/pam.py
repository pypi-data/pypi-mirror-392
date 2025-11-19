#!/usr/bin/env python3
"""
PAM clusterer.
"""

import logging
from typing import Union, Optional

import numpy as np

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass
from pypassist.mixin.cachable import Cachable
from pypassist.dataclass.decorators.viewer import viewer

from ..clusterer import Clusterer
from ..mixin.medoid import MedoidMixin
from ...metric.sequence.base.metric import SequenceMetric
from ...metric.trajectory.base.metric import TrajectoryMetric

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class PAMClustererSettings:
    """
    Configuration settings for the PAMClusterer.

    Attributes:
        metric (Union[SequenceMetric, TrajectoryMetric, str]):
            The metric used for clustering. If a string identifier is provided,
            (e.g., from a YAML configuration), it will be resolved into an `SequenceMetric`
            or `TrajectoryMetric` object from the global configuration.
        n_clusters (int):
            The number of clusters to form. Must be greater than 0. Defaults to 2.
        max_iter (int):
            Maximum number of iterations for the swap phase. Must be greater than 0.
            Defaults to 50.
        distance_threshold (Optional[float]):
            Optional distance threshold for clustering. If specified, must be non-negative.
            Defaults to None.
        cluster_column (str):
            The column name used to store the clustering results
            as a static feature. Defaults to "__PAM_CLUSTERS__".
    """

    metric: Union[SequenceMetric, TrajectoryMetric, str] = "linearpairwise"
    n_clusters: int = Field(default=2, gt=0)
    max_iter: int = Field(default=50, gt=0)
    distance_threshold: Optional[float] = None
    cluster_column: str = "__PAM_CLUSTERS__"

    @field_validator("distance_threshold")
    @classmethod
    def validate_distance_threshold(cls, v):
        """Validate that distance_threshold is non-negative if specified."""
        if v is None:
            return v

        v = float(v)

        if v < 0:
            raise ValueError("'distance_threshold' must be non-negative if specified.")

        return v


class PAMClusterer(MedoidMixin, Clusterer, register_name="pam"):
    """
    PAM (Partition Around Medoids) clustering implementation is a
    clustering algorithm similar to k-Medoids. In PAM, the medoids
    are *selected objects* (a subset of the complete list of
    objects to cluster).

    The goal of the algorithm is to minimize the inertia of the clustering
    ie. the average dissimilarity of objects to their closest selected object.

    .. important::

        The clustering technique is sound with metrics that hold distance's properties.
        More specifically, the triangular inegality must hold to ensure the convergence
        of the algorithm.
        A short loop detection is implemented in case of use with metrics without this
        property, but it does not protect to possible looping algorithm.

        The user is invited to set up the maximum iteration to avoid an infinite loop.

    .. warning::

        The method requires to precompute the distance matrix. It can be heavy in memory
        for large datasets.
        In such case, we invite the user to choose the CLARA clusterer.

    Example:

        Clustering with PAM, with 5 clusters and a linear pairwise metric.

        >>>    cluster_settings = PAMClustererSettings(metric="linearpairwise", n_clusters=5)
        >>>    clusterer = PAMClusterer(settings=cluster_settings)
        >>>    clusterer.fit(pool)


    .. seealso::

        :py:class:`CLARAClusterer`
            Implementation of the CLARA clusterer which is a sampled version of PAM clusterer.

    """

    SETTINGS_DATACLASS = PAMClustererSettings

    def __init__(self, settings=None, *, workenv=None):
        """
        Initialize the PAM clusterer with the given settings.

        Args:
            settings: Configuration settings for the PAM clusterer.
                If None, default PAMClustererSettings will be used.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        if settings is None:
            settings = PAMClustererSettings()

        Clusterer.__init__(self, settings, workenv=workenv)
        MedoidMixin.__init__(self)

    @Cachable.caching_method()
    def _compute_fit(self, metric, pool):
        """
        Computes and applies the clustering model to the data.
        The implementation of PAM is derived from this document:
        https://www.cs.umb.edu/cs738/pam1.pdf

        The function computes the clusters and set the `self._cluster`
        attribute with the results. In addition, it set the specific
        `self._medoids` attribute.

        Args:
            metric: The metric to compute distances between data points.
            pool: The data pool (sequence or trajectory data).
            model: The clustering model to use.
        """
        # compute the distance matrix
        dist_matrix = metric.collect_as_matrix(pool)
        pool_idx = list(dist_matrix.columns)  # save the id of the pool objects

        np_dist_matrix = dist_matrix.to_numpy()
        del dist_matrix  # free memory
        selected_list, unselected_list = self._pam_built(np_dist_matrix)
        n_iter = 0
        swap = self._pam_swap(selected_list, unselected_list, np_dist_matrix)
        while self.settings.max_iter and n_iter < self.settings.max_iter and swap:
            # apply the swap
            selected_list.remove(swap[0])
            selected_list.append(swap[1])
            unselected_list.remove(swap[1])
            unselected_list.append(swap[0])
            # try another swap
            n_iter += 1
            old_swap = swap
            swap = self._pam_swap(selected_list, unselected_list, np_dist_matrix)

            # detecting loop
            if swap and old_swap[0] == swap[1] and old_swap[1] == swap[0]:
                logging.warning("PAM stopped due to loop")
                break

        # save medoids and create clusters
        medoids_idx = selected_list
        self._medoids = [pool_idx[ix] for ix in medoids_idx]
        labels = np.argmin(np_dist_matrix[:, medoids_idx], axis=1)
        self._create_clusters(labels, pool_idx)

    def _pam_built(self, np_dist_matrix):
        """Compute the initial set of medoids

        Returns
            list[int]: a list of $k$ selected objects has medoids
            list[int]: a complementary list of unselected objects
        """
        selected_list = []
        unselected_list = list(range(len(np_dist_matrix)))
        # get the first medoid that minimize its distance to the others
        i0 = np.argmin(np.sum(np_dist_matrix, axis=0))
        selected_list.append(int(i0))
        unselected_list.remove(int(i0))

        # now we incrementally add other medoids
        while len(selected_list) < self.settings.n_clusters:
            # Sort only for deterministic numpy indexing
            selected_sorted = sorted(selected_list)
            unselected_sorted = sorted(unselected_list)

            # gain_matrix is the difference between Dj and d(i,j) for unselected objects
            gain_matrix = np_dist_matrix[
                np.ix_(unselected_sorted, unselected_sorted)
            ] - np.repeat(
                np.expand_dims(
                    np.min(
                        np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)],
                        axis=1,
                    ),
                    axis=1,
                ),
                len(unselected_sorted),
                axis=1,
            )
            gain_matrix[gain_matrix < 0] = 0
            tia = np.argmin(np.sum(gain_matrix, axis=1))
            # Find the actual index value from sorted list
            selected_value = unselected_sorted[tia]
            selected_list.append(selected_value)
            unselected_list.remove(selected_value)
        return selected_list, unselected_list

    def _pam_swap(self, selected_list, unselected_list, np_dist_matrix):
        """Attempt to improve the set of selected objects by swapping two objects
        The function evaluates the improvement of the clustering inertia by swapping
        an selected object by another unselected object.

        If the improvement reduces the inertia, it is an interesting change, otherwise there
        is no improvement to expect.

        Args:
            selected_list (list[int]): list of selected medoids
            unselected_list (list[int]): list of non-selected objects
            np_dist_matrix( np.array ): distance matrix

        Returns:
            (i,h): a swap to improve the cluster or None, if no improvement is possible.
                i is the index of the selected object and h is the index of the unselected object
        """
        # Sort only for deterministic numpy indexing
        selected_sorted = sorted(selected_list)
        unselected_sorted = sorted(unselected_list)

        # first compute the minimal distance, and the second minimal distance to the medoids
        min_dist = np.min(
            np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)], axis=1
        )
        second_min = np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)].copy()
        second_min[
            np.arange(second_min.shape[0]),
            np.argmin(
                np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)], axis=1
            ),
        ] = float("inf")
        second_min_dist = np.min(second_min, axis=1)
        del second_min

        # cost_matrix represents intermediary values for Tih
        # indices are : j,i,h
        cost_matrix = np.repeat(
            np.expand_dims(
                np_dist_matrix[np.ix_(unselected_sorted, unselected_sorted)], axis=1
            ),
            len(selected_sorted),
            axis=1,
        )

        for j in range(len(unselected_sorted)):
            # -- case  d(j,i)>Dj: re-evaluate cost due to a switch
            i_idx = np.where(
                np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)][j, :]
                > min_dist[j]
            )[0]
            tmp = cost_matrix[j, i_idx, :] - min_dist[j]
            tmp[tmp > 0] = 0
            cost_matrix[j, i_idx, :] = tmp

            # -- case d(j,i)==Dj
            i_idx = np.where(
                np_dist_matrix[np.ix_(unselected_sorted, selected_sorted)][j, :]
                == min_dist[j]
            )[0]
            tmp = cost_matrix[j, i_idx, :]
            for x in np.nditer(tmp, op_flags=["readwrite"]):
                x[...] = min(x, second_min_dist[j])
            tmp = tmp - min_dist[j]
            cost_matrix[j, i_idx, :] = tmp

        total_cost = np.sum(cost_matrix, axis=0)
        if np.sum(total_cost < 0) > 0:
            (i_s, h_u) = np.unravel_index(total_cost.argmin(), total_cost.shape)
            return (int(selected_sorted[int(i_s)]), int(unselected_sorted[h_u]))
        return None
