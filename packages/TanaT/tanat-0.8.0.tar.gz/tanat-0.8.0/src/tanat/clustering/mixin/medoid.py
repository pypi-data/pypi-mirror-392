#!/usr/bin/env python3
"""
Medoid-based clustering mixin.
"""


class MedoidMixin:
    """
    Mixin for clusterers that use medoids (representative objects).

    Provides common functionality for medoid-based clustering algorithms.
    """

    def __init__(self):
        self._medoids = None

    @property
    def medoids(self):
        """
        Returns the list of medoids. None if not fitted.

        The list of medoids is made of pool indices that serve as
        representative objects for each cluster.

        Returns:
            list: List of medoid identifiers, or None if clustering not performed.
        """
        return self._medoids
