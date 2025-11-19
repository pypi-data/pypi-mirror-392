#!/usr/bin/env python3
"""State data transformer."""

import logging
import pandas as pd

from ..period.base import PeriodDataTransformer
from .......time.granularity import Granularity
from .......time.anchor import resolve_date_series_from_anchor
from .......visualization.sequence.type.distribution.enum import DistributionMode

LOGGER = logging.getLogger(__name__)


class StateDataTransformer(PeriodDataTransformer, register_name="state"):
    """Transformer for state sequences."""

    def _get_anchor_for_relative_data(self):
        """States always use start anchor for relative data."""
        return "start"

    def _standardized_data(self, drop_na, entity_features=None):
        """
        Process state data with automatic end time calculation.
        Sets end times from next state's start when end_column is None.
        """
        start_column = self.sequence_settings.start_column
        id_column = self.sequence_settings.id_column
        end_column = self.sequence_settings.end_column

        data = self._sequence.sequence_data
        needs_copy = False

        # Handle missing end times
        if end_column is None:
            needs_copy = True

        # Handle dropping NA values
        if drop_na:
            needs_copy = True

        # Create a copy only if necessary
        data_copy = data.copy() if needs_copy else data

        if end_column is None:
            # pylint: disable=protected-access
            end_col = self.sequence_settings._default_end_column
            default_end = self.sequence_settings.default_end_value
            data_copy[end_col] = data_copy.groupby(
                id_column, group_keys=False, observed=True
            )[start_column].shift(-1, fill_value=default_end)

        if drop_na:
            data_copy.dropna(how="any", inplace=True)

        col2keep = self.sequence_settings.get_sequence_data_columns(
            standardize=True, entity_features=entity_features
        )
        return data_copy[col2keep]

    def _to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform state data to temporal distribution.

        For state sequences, we create a temporal grid and count how many
        sequences are in each state at each time period (occupation approach).

        Args:
            mode (str): Distribution mode ('proportion', 'percentage', 'count')
            time_relative (bool): Whether to use relative time
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include

        Returns:
            pd.DataFrame: Temporal distribution data in long format
        """
        # Normalize mode
        distribution_mode = DistributionMode.from_str(mode)

        if time_relative:
            granularity = "unit"  # Use unit granularity for relative time
            data = self._to_relative_time(
                drop_na=drop_na, entity_features=entity_features
            )
        else:
            data = self._standardized_data(
                drop_na=drop_na, entity_features=entity_features
            )

        # Get column names
        start_col, end_col = self.sequence_settings.temporal_columns(standardize=True)
        entity_features = self._validate_and_filter_entity_features(entity_features)
        entity_col = (
            entity_features[0] if len(entity_features) == 1 else "combined_entity"
        )

        if len(entity_features) > 1:
            data[entity_col] = data[entity_features].astype(str).agg("_".join, axis=1)

        granularity = Granularity.from_str(granularity)

        # Create complete time range (handles both dates and floats)
        if granularity == Granularity.UNIT:
            # For relative time or numeric data, create a range of floats
            min_time = data[start_col].min()
            max_time = data[end_col].max()
            step = 1
            date_range = pd.Index(range(int(min_time), int(max_time) + 1, step))
        else:
            # For datetime data, use date_range
            freq = granularity.pandas_freq
            date_range = pd.date_range(
                start=data[start_col].min(), end=data[end_col].max(), freq=freq
            )

        # Get all unique states
        unique_states = data[entity_col].unique()

        # Create occupation matrix: periods x states
        occupation_matrix = pd.DataFrame(0, index=date_range, columns=unique_states)

        # Fill occupation matrix: for each sequence, mark periods where it's active
        for _, row in data.iterrows():
            start_time = row[start_col]
            end_time = row[end_col]
            state = row[entity_col]

            # Skip if invalid dates
            if pd.isna(start_time) or pd.isna(end_time):
                continue

            # Mark periods where this state is active
            mask = (date_range >= start_time) & (date_range <= end_time)
            occupation_matrix.loc[mask, state] += 1

        # Convert to long format and calculate percentages
        result_data = []
        for time_period in occupation_matrix.index:
            period_total = occupation_matrix.loc[time_period].sum()

            for state in unique_states:
                count = occupation_matrix.loc[time_period, state]

                # Calculate value based on mode
                if distribution_mode == DistributionMode.COUNT:
                    value = count
                elif period_total > 0:  # Avoid division by zero
                    if distribution_mode == DistributionMode.PROPORTION:
                        value = count / period_total
                    else:  # PERCENTAGE
                        value = (count / period_total) * 100
                else:
                    value = 0.0

                result_data.append(
                    {
                        "time_period": time_period,
                        "annotation": state,
                        self.settings.distribution_column: value,
                    }
                )

        return pd.DataFrame(result_data)

    def as_event(
        self,
        *,  # pylint: disable=unused-argument
        anchor="start",
        time_column="time",
        add_duration_feature=False,
        duration_column="duration",
    ):
        """
        Convert StateSequence to EventSequence.

        Extracts a single timestamp from each state based on anchor.
        Optionally adds duration as an entity feature.

        Args:
            anchor (str): Which timestamp to extract ("start" or "end").
                Default: "start".
            time_column (str): Name for the time column in the resulting EventSequence.
                Default: "time".
            add_duration_feature (bool): Whether to add duration (end - start) as
                an entity feature with proper duration metadata.
                Default: False.
            duration_column (str): Name for the duration feature column when
                add_duration_feature=True. Default: "duration".

        Returns:
            EventSequence or EventSequencePool: Converted sequence with optional
                duration feature.
        """
        # 1. Standardize data
        data = self._standardized_data(drop_na=False)
        sequence_settings = self.sequence_settings
        temporal_cols = sequence_settings.temporal_columns(standardize=True)

        # 2. Extract anchor timestamp
        anchor_series = resolve_date_series_from_anchor(data, temporal_cols, anchor)

        # 3. Create new data with single time column
        new_data = data.copy()
        new_data[time_column] = anchor_series

        # 4. Build settings for event sequence
        event_settings = self._build_sequence_settings(time_column=time_column)

        # 5. Add duration feature if requested (BEFORE dropping temporal columns)
        if add_duration_feature:
            duration_series = self._calculate_duration_column(new_data, temporal_cols)
            new_data[duration_column] = duration_series
            event_settings = self._add_duration_to_settings(
                event_settings, duration_column
            )

        # 6. Clean up temporal columns
        new_data = new_data.drop(columns=temporal_cols)

        # 7. Create converted sequence
        return self._create_converted_sequence("event", new_data, event_settings)

    def as_state(self, *, end_value=None, start_column="start", end_column="end"):
        """
        Return the sequence itself (already a StateSequence).

        Args:
            end_value: Ignored (kept for signature consistency)
            start_column: Ignored (kept for signature consistency)
            end_column: Ignored (kept for signature consistency)
        """
        return self._sequence

    def as_interval(
        self,
        *,  # pylint: disable=unused-argument
        duration=None,
        start_column="start",
        end_column="end",
        drop_duration_feature=False,
    ):
        """
        Convert StateSequence to IntervalSequence.

        Trivial conversion (both types have start/end structure).

        Args:
            duration: Ignored (kept for signature consistency).
            start_column (str): Name for the start column in the resulting IntervalSequence.
                Default: "start".
            end_column (str): Name for the end column in the resulting IntervalSequence.
                Default: "end".
            drop_duration_feature (bool): Ignored (kept for signature consistency).

        Returns:
            IntervalSequence or IntervalSequencePool: Converted sequence.
        """
        sequence_settings = self.sequence_settings
        temporal_cols = sequence_settings.temporal_columns(standardize=True)

        # Get data with standardized columns
        data = self._standardized_data(drop_na=False)
        new_data = data.copy()

        # Rename temporal columns if needed
        self._rename_temporal_columns(
            new_data, temporal_cols, {"start": start_column, "end": end_column}
        )

        # Build settings and create sequence
        interval_settings = self._build_sequence_settings(
            start_column=start_column,
            end_column=end_column,
        )

        return self._create_converted_sequence("interval", new_data, interval_settings)
