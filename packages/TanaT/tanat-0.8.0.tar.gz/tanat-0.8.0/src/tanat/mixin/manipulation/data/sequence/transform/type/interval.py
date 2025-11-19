#!/usr/bin/env python3
"""Interval data transformer."""

import logging

from ..period.base import PeriodDataTransformer
from .......time.anchor import resolve_date_series_from_anchor

LOGGER = logging.getLogger(__name__)


class IntervalDataTransformer(PeriodDataTransformer, register_name="interval"):
    """Transformer for interval sequences."""

    def _get_anchor_for_relative_data(self):
        """Intervals use configurable anchor from settings."""
        return self.sequence_settings.anchor

    def _standardized_data(self, drop_na, entity_features=None):
        """Process interval data using basic standardization pattern."""
        return self._get_basic_standardized_data(drop_na, entity_features)

    def _to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """Distribution not supported for intervals."""
        raise NotImplementedError(
            f"to_distribution() is not supported for {type(self).__name__}"
        )

    def as_event(
        self,
        *,
        anchor="start",
        time_column="time",
        add_duration_feature=False,
        duration_column="duration",
    ):
        """
        Convert IntervalSequence to EventSequence.

        Extracts a single timestamp from each interval based on anchor.
        Optionally adds duration as an entity feature.

        Args:
            anchor (str): Which timestamp to extract ("start", "end", or "middle").
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

    def as_state(
        self,
        *,  # pylint: disable=unused-argument
        end_value=None,
        start_column="start",
        end_column="end",
    ):
        """
        Convert IntervalSequence to StateSequence.

        NOT SUPPORTED: Ambiguous due to potential overlaps and gaps.
        Use .as_event(anchor='start').as_state() for non-overlapping intervals.
        """
        raise NotImplementedError(
            "IntervalSequence.as_state() not supported.\n"
            "Use `.as_event(anchor='start').as_state()` for non-overlapping intervals."
        )

    def as_interval(
        self,
        *,  # pylint: disable=unused-argument
        duration=None,
        start_column="start",
        end_column="end",
        drop_duration_feature=False,
    ):
        """
        Return the sequence itself (already an IntervalSequence).

        Args:
            duration: Ignored (kept for signature consistency).
            start_column (str): Ignored (kept for signature consistency).
            end_column (str): Ignored (kept for signature consistency).
            drop_duration_feature (bool): Ignored (kept for signature consistency).

        Returns:
            IntervalSequence or IntervalSequencePool: The sequence itself (no copy).
        """
        return self._sequence
