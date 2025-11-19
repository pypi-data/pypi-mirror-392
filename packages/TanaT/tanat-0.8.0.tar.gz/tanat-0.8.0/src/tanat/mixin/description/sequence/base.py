#!/usr/bin/env python3
"""Base descriptor for sequence descriptions."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Optional, Union

import pandas as pd
import numpy as np

from pypassist.mixin.registrable import Registrable
from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin

LOGGER = logging.getLogger(__name__)


### --- Define metric categories ---
INTEGER_METRICS = frozenset(
    [
        "length",
        "vocabulary_size",
        "n_transitions",
        "n_sequences",
    ]
)

FLOAT_METRICS = frozenset(
    [
        "entropy",
    ]
)

DURATION_METRICS = frozenset(
    [
        "temporal_span",
        "mean_duration",
        "median_duration",
        "duration_std",
        "gap_std",
        "median_gap",
    ]
)
### --- End metric categories ---


@dataclass
class BaseSequenceDescription:
    """
    Common metrics for all sequence types.

    Attributes:
        length: Number of entities in the sequence.
        entropy: Shannon entropy of entity features.
        vocabulary_size: Number of distinct entities.
        temporal_span: Time difference between first and last event.
    """

    length: Optional[Union[int, pd.Series]] = None
    entropy: Optional[Union[float, pd.Series]] = None
    vocabulary_size: Optional[Union[int, pd.Series]] = None
    temporal_span: Optional[Union[pd.Timedelta, pd.Series]] = None

    def to_metadata(self, prefix=""):
        """
        Generate metadata dictionary for description metrics.

        Args:
            prefix: Prefix to add to all column names.

        Returns:
            dict: Metadata dictionary with format:
                {
                    'column_name': {
                        'dtype': 'numerical',
                        'settings': {
                            'dtype': 'Int32' or 'float32',
                            'min_value': float,
                            'max_value': float,
                        }
                    }
                }
        """

        metadata = {}

        for field_name, field_value in self.__dict__.items():
            column_name = f"{prefix}{field_name}" if prefix else field_name

            # Extract min/max values
            if isinstance(field_value, pd.Series):
                min_val = field_value.min()
                max_val = field_value.max()
            else:
                # Scalar value (int, float, numpy scalar, timedelta, etc.)
                min_val = max_val = field_value

            if pd.isna(min_val):
                min_val = None
            if pd.isna(max_val):
                max_val = None

            # Determine metric type and create appropriate metadata
            if field_name in DURATION_METRICS:
                metadata[column_name] = {
                    "feature_type": "duration",
                    "settings": {
                        "granularity": "day",
                        "min_value": min_val,
                        "max_value": max_val,
                    },
                }
            elif field_name in INTEGER_METRICS:
                metadata[column_name] = {
                    "feature_type": "numerical",
                    "settings": {
                        "dtype": "Int32",
                        "min_value": min_val,
                        "max_value": max_val,
                    },
                }
            elif field_name in FLOAT_METRICS:
                metadata[column_name] = {
                    "feature_type": "numerical",
                    "settings": {
                        "dtype": "Float32",
                        "min_value": min_val,
                        "max_value": max_val,
                    },
                }
            else:
                # Fallback: Float32 for unknown metrics
                metadata[column_name] = {
                    "feature_type": "numerical",
                    "settings": {
                        "dtype": "Float32",
                        "min_value": min_val,
                        "max_value": max_val,
                    },
                }

        return metadata

    def to_dataframe(self, sequence_id=None, index_name=None):
        """
        Convert description to DataFrame.

        Args:
            sequence_id: Optional sequence ID to use as index for single sequence.
                If None and all values are scalars, uses index=[0].
            index_name: Optional name for the DataFrame index.
                If provided, ensures the index has this name.

        Returns:
            pd.DataFrame: Metrics as columns, sequence IDs as index.
                - For single sequence: 1 row DataFrame.
                - For pool: N rows DataFrame.
        """
        data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                data[field.name] = value

        # Check if all values are scalars (single sequence case)
        if data and all(not isinstance(v, pd.Series) for v in data.values()):
            # All scalars: create DataFrame with single row
            # Use provided sequence_id or default to 0
            index = [sequence_id] if sequence_id is not None else [0]
            df = pd.DataFrame(data, index=index)
        else:
            # Mixed or all Series: let pandas infer structure
            df = pd.DataFrame(data)

        # Set index name if provided
        if index_name is not None:
            df.index.name = index_name

        return df


class SequenceDescriptor(
    ABC,
    Cachable,
    SettingsMixin,
    Registrable,
):
    """
    Interface for type-specific sequence data description.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"

    def __init__(self, sequence, settings=None):
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        self._sequence = sequence

    @classmethod
    def init(cls, descriptor_type, sequence, settings=None):
        """
        Initialize the descriptor for a specific type.

        Args:
            descriptor_type:
                The descriptor type.

            sequence:
                The sequence or sequence pool to describe.

            settings:
                Optional settings for the descriptor. If not provided,
                defaults from the descriptor's dataclass will be used.

        Returns:
            An instance of the descriptor.
        """
        return cls.get_registered(descriptor_type)(sequence, settings)

    @Cachable.caching_method()
    def describe(self, dropna=False):
        """
        Compute and return the sequence description.

        Args:
            dropna (bool): If True, silently drops NaT values in temporal columns.
                If False, raises ValueError when NaT values are encountered.
                Default: False.

        Returns:
            BaseSequenceDescription: Computed description with metrics.
        """
        return self._compute_description(dropna=dropna)

    @abstractmethod
    def _compute_description(self, dropna=False):
        """
        Internal abstract method to compute the description.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Must be implemented by subclasses to return a BaseSequenceDescription instance.
        """

    @Cachable.caching_method()
    def _compute_length(self):
        """
        Compute the length (number of entities) per sequence.

        Returns:
            Union[int, pd.Series]:
                - int: For single sequence
                - pd.Series: For pool (indexed by sequence_id)
        """
        data = self._sequence.sequence_data

        # Group by index (sequence_id) and count rows
        grouped_length = data.groupby(level=0).size()

        # If single sequence, return scalar
        if len(grouped_length) == 1:
            return int(grouped_length.iloc[0])

        # If pool, return Series
        return grouped_length

    @Cachable.caching_method()
    def _compute_entropy(self):
        """
        Compute Shannon entropy of entity features per sequence.

        Returns:
            Union[float, pd.Series]:
                - float: For single sequence
                - pd.Series: For pool (indexed by sequence_id)

        Note:
            Entropy is computed on the entity_features columns.
            H(X) = -Σ p(x) * log2(p(x))
            Returns 0 for sequences with a single unique value.
        """
        data = self._sequence.sequence_data
        entity_features = self._sequence.settings.entity_features

        def compute_entropy_for_sequence(seq_df):
            """Compute entropy for a single sequence."""
            # Get entity feature values as tuples (for multiple features)
            if len(entity_features) > 1:
                values = seq_df[entity_features].apply(tuple, axis=1)
            else:
                values = seq_df[entity_features[0]]

            # Count occurrences
            value_counts = values.value_counts()

            # Filter out zero counts (can happen with categorical dtypes)
            value_counts = value_counts[value_counts > 0]

            # If only one unique value, entropy is 0
            if len(value_counts) <= 1:
                return 0.0

            probabilities = value_counts / len(seq_df)

            # Compute Shannon entropy: H(X) = -Σ p(x) * log2(p(x))
            entropy = -np.sum(probabilities * np.log2(probabilities))

            # Ensure no negative zero
            return float(abs(entropy))

        # Group by sequence_id and compute entropy
        grouped_entropy = data.groupby(level=0).apply(compute_entropy_for_sequence)

        # If single sequence, return scalar
        if len(grouped_entropy) == 1:
            return float(grouped_entropy.iloc[0])

        # If pool, return Series
        return grouped_entropy

    @Cachable.caching_method()
    def _compute_vocabulary_size(self):
        """
        Compute the number of distinct entities per sequence.

        Returns:
            Union[int, pd.Series]:
                - int: For single sequence
                - pd.Series: For pool (indexed by sequence_id)
        """
        data = self._sequence.sequence_data
        entity_features = self._sequence.settings.entity_features

        def compute_vocab_for_sequence(seq_df):
            """Compute vocabulary size for a single sequence."""
            # Get entity feature values as tuples (for multiple features)
            if len(entity_features) > 1:
                values = seq_df[entity_features].apply(tuple, axis=1)
            else:
                values = seq_df[entity_features[0]]

            # Count unique values
            return values.nunique()

        # Group by sequence_id and compute vocabulary size
        grouped_vocab = data.groupby(level=0).apply(compute_vocab_for_sequence)

        # If single sequence, return scalar
        if len(grouped_vocab) == 1:
            return int(grouped_vocab.iloc[0])

        # If pool, return Series
        return grouped_vocab

    @Cachable.caching_method()
    def _compute_temporal_span(self):
        """
        Compute the temporal extent of the sequence (max timestamp - min timestamp).

        Returns:
            Union[pd.Timedelta, pd.Series]:
                - pd.Timedelta: For single sequence
                - pd.Series of Timedelta: For pool (indexed by sequence_id)
        """
        # Get standardized data with guaranteed temporal columns
        # pylint: disable=protected-access
        data = self._sequence._get_standardized_data()
        temporal_cols = self._sequence.settings.temporal_columns(standardize=True)

        if len(temporal_cols) == 1:
            # EventSequence: single time column
            time_col = temporal_cols[0]

            def compute_span(seq_df):
                return seq_df[time_col].max() - seq_df[time_col].min()

        elif len(temporal_cols) == 2:
            # StateSequence or IntervalSequence: start and end columns
            start_col, end_col = temporal_cols

            def compute_span(seq_df):
                # Span from earliest start to latest end
                return seq_df[end_col].max() - seq_df[start_col].min()

        else:
            raise ValueError(
                f"Unexpected number of temporal columns: {len(temporal_cols)}"
            )

        # Group by sequence_id and compute temporal span
        grouped_span = data.groupby(level=0).apply(compute_span)

        # If single sequence, return scalar Timedelta
        if len(grouped_span) == 1:
            return grouped_span.iloc[0]

        # If pool, return Series
        return grouped_span

    @Cachable.caching_method()
    def _compute_durations(self, dropna=False):
        """
        Compute the duration of each state or interval in the sequence.

        Args:
            dropna (bool): If True, silently drops NaT values in temporal columns.
                If False, raises ValueError when NaT values are encountered.
                Default: False.

        Returns:
            pd.Series: Duration for each state or interval (with multi-index).

        Raises:
            ValueError: If dropna=False and NaT values are found in durations.
        """
        # pylint: disable=protected-access
        # Get standardized data
        data = self._sequence._get_standardized_data()
        time_cols = self._sequence.settings.temporal_columns(standardize=True)
        start_col, end_col = time_cols[0], time_cols[1]

        # If dropna=False, check for NaT values in temporal columns before computation
        if not dropna:
            n_nat = data[[start_col, end_col]].isna().sum().sum()
            if n_nat > 0:
                raise ValueError(
                    f"Found {n_nat} NaT value(s) in temporal columns. "
                    f"Use describe(dropna=True) to ignore these values."
                )

        # Drop rows with NaT in temporal columns only (preserves rows with NA in entity features)
        if dropna:
            data = data.dropna(subset=[start_col, end_col])

        durations = data[end_col] - data[start_col]

        return durations

    @Cachable.caching_method()
    def _compute_mean_duration(self, dropna=False):
        """
        Compute the mean duration of states or intervals.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            pd.Timedelta or pd.Series: Mean duration per sequence.
        """
        durations = self._compute_durations(dropna=dropna)
        grouped = durations.groupby(level=0).mean()

        # If single sequence, return scalar
        if len(grouped) == 1:
            return grouped.iloc[0]

        # If pool, return Series
        return grouped

    @Cachable.caching_method()
    def _compute_median_duration(self, dropna=False):
        """
        Compute the median duration of states or intervals.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            pd.Timedelta or pd.Series: Median duration per sequence.
        """
        durations = self._compute_durations(dropna=dropna)
        grouped = durations.groupby(level=0).median()

        # If single sequence, return scalar
        if len(grouped) == 1:
            return grouped.iloc[0]

        # If pool, return Series
        return grouped

    @Cachable.caching_method()
    def _compute_duration_std(self, dropna=False):
        """
        Compute the standard deviation of durations.

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            pd.Timedelta or pd.Series: Standard deviation of durations per sequence.
        """
        durations = self._compute_durations(dropna=dropna)
        grouped = durations.groupby(level=0).std()

        # If single sequence, return scalar
        if len(grouped) == 1:
            return grouped.iloc[0]

        # If pool, return Series
        return grouped
