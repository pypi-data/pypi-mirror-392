#!/usr/bin/env python3
"""State sequence descriptor."""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from pypassist.mixin.cachable import Cachable

from ..base import SequenceDescriptor, BaseSequenceDescription


@dataclass
class StateSequenceDescription(BaseSequenceDescription):
    """
    Description for StateSequence.

    Attributes:
        n_transitions: Number of state changes in the sequence.
        cycle_rate: Rate of state cycling (reserved for future use).
        mean_duration: Average duration of states.
        median_duration: Median duration of states.
        duration_std: Standard deviation of state durations.

    Note:
        Inherits from BaseSequenceDescription: length, entropy, vocabulary_size, temporal_span.
    """

    n_transitions: Optional[Union[int, pd.Series]] = None
    cycle_rate: Optional[Union[float, pd.Series]] = None
    mean_duration: Optional[Union[pd.Timedelta, pd.Series]] = None
    median_duration: Optional[Union[pd.Timedelta, pd.Series]] = None
    duration_std: Optional[Union[pd.Timedelta, pd.Series]] = None


class StateSequenceDescriptor(SequenceDescriptor, register_name="state"):
    """Descriptor for StateSequence."""

    SETTINGS_DATACLASS = StateSequenceDescription

    def __init__(self, sequence, settings=None):
        if settings is None:
            settings = StateSequenceDescription()
        SequenceDescriptor.__init__(self, sequence, settings)

    def _compute_description(self, dropna=False):
        """
        Compute the description for a state sequence.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            StateSequenceDescription: Description with computed metrics.
        """
        return StateSequenceDescription(
            length=self._compute_length(),
            entropy=self._compute_entropy(),
            vocabulary_size=self._compute_vocabulary_size(),
            temporal_span=self._compute_temporal_span(),
            n_transitions=self._compute_n_transitions(),
            mean_duration=self._compute_mean_duration(dropna=dropna),
            median_duration=self._compute_median_duration(dropna=dropna),
            duration_std=self._compute_duration_std(dropna=dropna),
        )

    @Cachable.caching_method()
    def _compute_n_transitions(self):
        """
        Compute the number of state transitions.

        Returns:
            Union[int, pd.Series]:
                - int: For single sequence
                - pd.Series: For pool (indexed by sequence_id)

        Note:
            Counts the number of times the state changes (state[i] != state[i-1]).
            A sequence with constant state has 0 transitions.
            Example: [A, A, B, C, C] has 2 transitions (A→B and B→C).
        """
        data = self._sequence.sequence_data
        entity_features = self._sequence.settings.entity_features

        def count_transitions(seq_df):
            """Count transitions for a single sequence."""
            if len(seq_df) < 2:
                return 0

            # Get state values as tuples (for multiple features)
            if len(entity_features) > 1:
                states = seq_df[entity_features].apply(tuple, axis=1).values
            else:
                states = seq_df[entity_features[0]].values

            # Count changes between consecutive states
            # Compare states[i] with states[i-1] for i in [1, n)
            transitions = (states[1:] != states[:-1]).sum()
            return int(transitions)

        # Group by sequence_id and count transitions
        grouped_transitions = data.groupby(level=0).apply(count_transitions)

        # If single sequence, return scalar
        if len(grouped_transitions) == 1:
            return int(grouped_transitions.iloc[0])

        # If pool, return Series
        return grouped_transitions
