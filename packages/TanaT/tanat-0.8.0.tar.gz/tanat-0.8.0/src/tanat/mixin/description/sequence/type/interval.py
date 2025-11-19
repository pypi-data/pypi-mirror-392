#!/usr/bin/env python3
"""Interval sequence descriptor."""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from ..base import SequenceDescriptor, BaseSequenceDescription


@dataclass
class IntervalSequenceDescription(BaseSequenceDescription):
    """
    Description for IntervalSequence.

    Attributes:
        mean_duration: Average duration of intervals.
        median_duration: Median duration of intervals.
        duration_std: Standard deviation of interval durations.

    Note:
        Inherits from BaseSequenceDescription: length, entropy, vocabulary_size, temporal_span.
    """

    mean_duration: Optional[Union[pd.Timedelta, pd.Series]] = None
    median_duration: Optional[Union[pd.Timedelta, pd.Series]] = None
    duration_std: Optional[Union[pd.Timedelta, pd.Series]] = None


class IntervalSequenceDescriptor(SequenceDescriptor, register_name="interval"):
    """Descriptor for IntervalSequence."""

    SETTINGS_DATACLASS = IntervalSequenceDescription

    def __init__(self, sequence, settings=None):
        if settings is None:
            settings = IntervalSequenceDescription()
        SequenceDescriptor.__init__(self, sequence, settings)

    def _compute_description(self, dropna=False):
        """
        Compute the description for an interval sequence.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            IntervalSequenceDescription: Description with computed metrics.
        """
        return IntervalSequenceDescription(
            length=self._compute_length(),
            entropy=self._compute_entropy(),
            vocabulary_size=self._compute_vocabulary_size(),
            temporal_span=self._compute_temporal_span(),
            mean_duration=self._compute_mean_duration(dropna=dropna),
            median_duration=self._compute_median_duration(dropna=dropna),
            duration_std=self._compute_duration_std(dropna=dropna),
        )
