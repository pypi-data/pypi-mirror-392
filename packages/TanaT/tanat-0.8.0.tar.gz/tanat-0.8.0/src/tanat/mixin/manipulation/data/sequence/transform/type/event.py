#!/usr/bin/env python3
"""
Event data transformer.
"""

import logging
from datetime import timedelta

import pandas as pd

from ..base import SequenceDataTransformer
from .......time.duration import calculate_duration_from_series

LOGGER = logging.getLogger(__name__)


class EventDataTransformer(SequenceDataTransformer, register_name="event"):
    """
    Transformer for event sequences.
    """

    def _standardized_data(self, drop_na, entity_features=None):
        """Process event data using basic standardization pattern."""
        return self._get_basic_standardized_data(drop_na, entity_features)

    def _to_relative_time(
        self,
        drop_na=False,
        entity_features=None,
        tmp_t0_col="__TMP_T0__",
    ):
        """
        Transform event data to relative time based on t_zero.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.
            tmp_t0_col (str, optional): Temporary t0 column name


        Returns:
            pd.DataFrame: Transformed data
        """
        # -- Set reference dates from t_zero
        sequence_data_copy = self._standardized_data(
            drop_na=drop_na, entity_features=entity_features
        )
        if not drop_na:  # make sure it is a copy
            sequence_data_copy = sequence_data_copy.copy()
        t_zero = self._sequence.t_zero
        sequence_data_copy = self._add_t0_column(sequence_data_copy, t_zero, tmp_t0_col)
        sequence_settings = self.sequence_settings

        # -- Calculate duration from t_zero to event timestamp
        granularity = self._sequence.granularity
        duration_series = calculate_duration_from_series(
            start_series=sequence_data_copy[tmp_t0_col],
            end_series=sequence_data_copy[sequence_settings.time_column],
            granularity=granularity,
        )

        relative_time_column = self.sequence_settings.time_column
        sequence_data_copy[relative_time_column] = duration_series.values

        # -- Clean up useless temporal columns
        col2drop = [tmp_t0_col]
        sequence_data_copy = self._cleanup_temporal_columns(
            sequence_data_copy, col2drop
        )

        return sequence_data_copy

    def _standardize_relative_data(self, drop_na=False, entity_features=None):
        """
        Standardize relative data for event sequences.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Standardized DataFrame
        """
        relative_df = self._to_relative_time(
            drop_na=drop_na, entity_features=entity_features
        )
        relative_df.rename(
            columns={
                self.sequence_settings.time_column: self.settings.relative_time_column,
            },
            inplace=True,
        )
        return relative_df

    def _to_time_spent(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform sequence data to time spent for event sequences.

        For events, the duration is calculated as an occurrence.

        Args:
            by_id (bool): Whether to group by the id column.
            granularity (str): Time unit for the time spent values.
                Useless for events, but kept for consistency.
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list): List of entity features to include in the calculation.
            If None, all features specified in the sequence settings will be used.

        Returns:
            pd.DataFrame: DataFrame with time spent values.
        """
        entity_features = self._validate_and_filter_entity_features(entity_features)
        occurrence_data = self.to_occurrence(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )
        result = occurrence_data.copy()
        occurrence_col = self.settings.occurrence_column
        time_spent_col = self.settings.time_spent_column
        result.rename(
            columns={occurrence_col: time_spent_col},
            inplace=True,
        )

        return result

    def _to_distribution(
        self,
        # pylint:disable=unused-argument
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform event data to temporal distribution.

        Not supported for event sequences.

        Raises:
            NotImplementedError: Always raised for event sequences
        """
        raise NotImplementedError(
            f"to_distribution() is currently only supported for StateSequencePool. "
            f"Current type: {type(self).__name__}"
        )

    def as_event(
        self,
        *,  # pylint: disable=unused-argument
        anchor="start",
        time_column="time",
        add_duration_feature=False,
        duration_column="duration",
    ):
        """
        Return the sequence itself (already an EventSequence).

        Args:
            anchor (str): Ignored (kept for signature consistency).
            time_column (str): Ignored (kept for signature consistency).
            add_duration_feature (bool): Ignored (kept for signature consistency).
            duration_column (str): Ignored (kept for signature consistency).

        Returns:
            EventSequence or EventSequencePool: The sequence itself (no copy).
        """
        return self._sequence

    def as_state(self, *, end_value=None, start_column="start", end_column="end"):
        """
        Convert EventSequence to StateSequence.

        Creates states from consecutive events. Each event becomes the start of a state,
        which ends when the next event occurs. The final state's end is controlled by end_value.

        Args:
            end_value: Value for the final state's end time (None, datetime, or int).
                       If None, the last state will have no explicit end time.
            start_column: Name for the start column in the resulting StateSequence
            end_column: Name for the end column in the resulting StateSequence

        Returns:
            StateSequence or StateSequencePool: Converted sequence with state structure
        """
        sequence_settings = self.sequence_settings

        # Get standardized data and rename time column to start_column
        new_data = self._standardized_data(drop_na=False).copy()
        temporal_cols = sequence_settings.temporal_columns(standardize=True)

        # Rename temporal column
        self._rename_temporal_columns(new_data, temporal_cols, {"time": start_column})

        # Create end_column by shifting start times within each ID group
        id_column = sequence_settings.id_column
        new_data[end_column] = new_data.groupby(
            id_column, group_keys=False, observed=True
        )[start_column].shift(-1, fill_value=end_value)

        # Build settings and create sequence
        state_settings = self._build_sequence_settings(
            start_column=start_column,
            end_column=end_column,
            default_end_value=end_value,
        )

        return self._create_converted_sequence("state", new_data, state_settings)

    def as_interval(
        self,
        *,
        duration=None,
        start_column="start",
        end_column="end",
        drop_duration_feature=False,
    ):
        """
        Convert EventSequence to IntervalSequence.

        Creates intervals by adding a duration to each event timestamp. Each event becomes
        the start of an interval, with end = start + duration.

        Args:
            duration: Duration specification (REQUIRED). Can be:
                - timedelta/DateOffset: Fixed duration for all events
                  (e.g., timedelta(hours=8) or pd.DateOffset(months=3))
                - int/float: Fixed numeric duration (for timestep-based sequences)
                - str: Column name (must be entity feature with duration metadata)
                - pd.Series: Duration values (must match data length)
            start_column (str): Name for the start column in the resulting IntervalSequence.
                Default: "start".
            end_column (str): Name for the end column in the resulting IntervalSequence.
                Default: "end".
            drop_duration_feature (bool): Whether to drop the duration feature after conversion.
                Only applies when duration is a string (feature name).
                If True, the duration feature is removed from entity_features.
                Default: False.

        Returns:
            IntervalSequence or IntervalSequencePool: Converted sequence with intervals.

        Raises:
            NotImplementedError: If duration is None (duration is required).
            ValueError: If duration column validation fails or Series length mismatch.
        """
        if duration is None:
            raise NotImplementedError(
                "EventSequence.as_interval() requires a duration parameter.\n"
                "Provide: timedelta/DateOffset/numeric (fixed), str (column name), or Series."
            )

        # 1. Standardize data
        new_data = self._standardized_data(drop_na=False).copy()
        sequence_settings = self.sequence_settings
        temporal_cols = sequence_settings.temporal_columns(standardize=True)

        # 2. Resolve duration to Series
        duration_series = self._resolve_duration(new_data, duration)

        # 3. Transform temporal columns
        self._rename_temporal_columns(new_data, temporal_cols, {"time": start_column})
        new_data[end_column] = new_data[start_column] + duration_series

        # 4. Build settings for interval sequence
        interval_settings = self._build_sequence_settings(
            start_column=start_column,
            end_column=end_column,
        )

        # 5. Drop duration feature if requested
        if drop_duration_feature and isinstance(duration, str):
            interval_settings = self._remove_feature_from_settings(
                interval_settings, duration
            )

        # 6. Create converted sequence
        return self._create_converted_sequence("interval", new_data, interval_settings)

    def _validate_duration_column(self, duration_column):
        """
        Validate that duration column is properly configured.

        Args:
            duration_column: Column name to validate

        Raises:
            ValueError: If validation fails
        """
        sequence_settings = self.sequence_settings

        # Validation 1: Must be an entity feature
        if duration_column not in sequence_settings.entity_features:
            raise ValueError(
                f"Duration column '{duration_column}' must be declared as an entity feature. "
                f"Available entity features: {sequence_settings.entity_features}"
            )

        # Validation 2: Must have duration feature type
        entity_descriptors = self._sequence.metadata.entity_descriptors
        feature_desc = entity_descriptors[duration_column]

        if feature_desc.feature_type != "duration":
            raise ValueError(
                f"Duration column '{duration_column}' must have feature_type='duration'. "
                f"Got: '{feature_desc.feature_type}'"
            )

    def _resolve_duration(self, data, duration):
        """
        Resolve duration parameter to a pandas Series.

        Args:
            data: DataFrame with event data (already standardized)
            duration: Duration specification. Can be:
                - str: Column name (entity feature with duration metadata)
                - pd.Series: Explicit duration values (must match length)
                - timedelta/DateOffset/numeric: Fixed duration for all events

        Returns:
            pd.Series: Duration values aligned with data index

        Raises:
            ValueError: If duration validation fails
        """
        # Case 1: Fixed duration (timedelta or DateOffset) → broadcast to all rows
        if isinstance(duration, (timedelta, pd.DateOffset)):
            return pd.Series(duration, index=data.index)

        # Case 1b: Numeric scalar → broadcast as float
        if isinstance(duration, (int, float)):
            return pd.Series(float(duration), index=data.index)

        # Case 2: Column name → validate and get it
        if isinstance(duration, str):
            self._validate_duration_column(duration)
            # Column is already coerced by DurationFeatureCoercer
            return data[duration]

        # Case 3: Series → validate length and use
        if isinstance(duration, pd.Series):
            if len(duration) != len(data):
                raise ValueError(
                    f"Duration Series length ({len(duration)}) must match "
                    f"data length ({len(data)})"
                )

            # Align with data index
            if not duration.index.equals(data.index):
                duration = pd.Series(duration.values, index=data.index)

            return duration

        # Invalid type
        raise ValueError(
            f"Invalid duration type: {type(duration).__name__}. "
            f"Expected: str (entity feature name), pd.Series, timedelta, pd.DateOffset, or numeric"
        )
