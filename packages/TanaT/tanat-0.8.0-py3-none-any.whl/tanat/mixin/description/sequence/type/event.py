#!/usr/bin/env python3
"""Event sequence descriptor."""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from pypassist.mixin.cachable import Cachable

from ..base import SequenceDescriptor, BaseSequenceDescription


@dataclass
class EventSequenceDescription(BaseSequenceDescription):
    """
    Description for EventSequence.

    Attributes:
        median_gap: Median time gap between consecutive events.
        gap_std: Standard deviation of time gaps between events.

    Note:
        Inherits from BaseSequenceDescription: length, entropy, vocabulary_size, temporal_span.
    """

    median_gap: Optional[Union[float, pd.Series]] = None
    gap_std: Optional[Union[float, pd.Series]] = None


class EventSequenceDescriptor(SequenceDescriptor, register_name="event"):
    """Descriptor for EventSequence."""

    SETTINGS_DATACLASS = EventSequenceDescription

    def __init__(self, sequence, settings=None):
        if settings is None:
            settings = EventSequenceDescription()
        SequenceDescriptor.__init__(self, sequence, settings)

    def _compute_description(self, dropna=False):
        """
        Compute the description for an event sequence.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            EventSequenceDescription: Description with computed metrics.
        """
        return EventSequenceDescription(
            length=self._compute_length(),
            entropy=self._compute_entropy(),
            vocabulary_size=self._compute_vocabulary_size(),
            temporal_span=self._compute_temporal_span(),
            median_gap=self._compute_median_gap(dropna=dropna),
            gap_std=self._compute_gap_std(dropna=dropna),
        )

    @Cachable.caching_method()
    def _compute_gaps(self, dropna=False):
        """
        Compute time gaps between consecutive events.

        Args:
            dropna (bool): If True, silently drops NaT values in time column.
                If False, raises ValueError when NaT values are encountered.
                Default: False.

        Returns:
            pd.Series: Time gaps between consecutive events.

        Raises:
            ValueError: If dropna=False and NaT values are found in gaps.
        """
        data = self._sequence.sequence_data
        time_col = self._sequence.settings.time_column

        # If dropna=False, check for NaT values in time column before computation
        if not dropna:
            n_nat = data[time_col].isna().sum()
            if n_nat > 0:
                raise ValueError(
                    f"Found {n_nat} NaT value(s) in time column. "
                    f"Use describe(dropna=True) to ignore these values."
                )

        # Drop rows with NaT in time column only (preserves rows with NA in entity features)
        if dropna:
            data = data.dropna(subset=[time_col])

        # Compute differences between consecutive timestamps
        # Skip first NaT (no previous event for first timestamp)
        gaps = data.groupby(level=0)[time_col].apply(lambda x: x.diff()[1:])

        return gaps

    @Cachable.caching_method()
    def _compute_median_gap(self, dropna=False):
        """
        Compute the median gap between consecutive events.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            Union[pd.Timedelta, pd.Series]: Median gap per sequence.

        Note:
            Returns pd.NaT for sequences with less than 2 events.
        """
        gaps = self._compute_gaps(dropna=dropna)

        if len(gaps) == 0:
            return pd.NaT

        # Group gaps by sequence_id and compute median
        grouped = gaps.groupby(level=0).median()

        # If single sequence, return scalar
        if len(grouped) == 1:
            return grouped.iloc[0]

        # If pool, return Series
        return grouped

    @Cachable.caching_method()
    def _compute_gap_std(self, dropna=False):
        """
        Compute the standard deviation of gaps between events.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            Union[pd.Timedelta, pd.Series]: Standard deviation of gaps per sequence.

        Note:
            Returns pd.NaT for sequences with less than 2 events.
        """
        gaps = self._compute_gaps(dropna=dropna)

        if len(gaps) == 0:
            return pd.NaT

        # Group gaps by sequence_id and compute std
        grouped = gaps.groupby(level=0).std()

        # If single sequence, return scalar
        if len(grouped) == 1:
            return grouped.iloc[0]

        # If pool, return Series
        return grouped
