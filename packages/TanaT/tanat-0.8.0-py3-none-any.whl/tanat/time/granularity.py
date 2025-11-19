#!/usr/bin/env python3
"""
Temporal granularity enumeration and utilities.
"""

import enum
import pandas as pd
from pypassist.enum.enum_str import EnumStrMixin


@enum.unique
class Granularity(EnumStrMixin, enum.Enum):
    """
    Temporal granularity units for time-based operations.

    Defines standard time units for precise temporal sequence generation
    and manipulation, with support for both fixed and calendar-aware
    time increments.

    Attributes:
        HOUR: Hourly time resolution.
        DAY: Daily time resolution.
        WEEK: Weekly time resolution.
        MONTH: Monthly time resolution (calendar-aware).
        YEAR: Yearly time resolution (calendar-aware).
    """

    UNIT = enum.auto()
    HOUR = enum.auto()
    DAY = enum.auto()
    WEEK = enum.auto()
    MONTH = enum.auto()
    YEAR = enum.auto()

    @property
    def pandas_freq(self):
        """Convert Granularity enum to pandas frequency string.

        Returns None for UNIT (abstract timestep-based units have no pandas frequency).
        """
        if self == Granularity.UNIT:
            return None

        freq_mapping = {
            Granularity.HOUR: "h",
            Granularity.DAY: "D",
            Granularity.WEEK: "W",
            Granularity.MONTH: "M",
            Granularity.YEAR: "Y",
        }
        return freq_mapping[self]

    @property
    def is_calendar_based(self):
        """
        Determine if the granularity is calendar-aware.

        Calendar-aware units (MONTH, YEAR) have variable durations
        based on calendar rules.
        """
        return self in [Granularity.MONTH, Granularity.YEAR]

    def to_offsets(self, values):
        """
        Convert values to time offset objects.

        Generates time increments based on the granularity:
        - UNIT: Returns values as floats (for timestep-based sequences)
        - Calendar units (MONTH, YEAR) use DateOffset
        - Fixed units (WEEK, DAY, HOUR) use Timedelta

        Args:
            values: Numeric values to convert

        Returns:
            Series of offsets (float for UNIT, DateOffset list for calendar, Timedelta Series for fixed)
        """
        # Timestep-based (abstract units) - return as floats, no conversion
        if self == Granularity.UNIT:
            result = pd.to_numeric(values, errors="raise")
            return result.astype("float")  # Nullable float type

        # Calendar-aware (variable duration)
        if self == Granularity.MONTH:
            return [pd.DateOffset(months=int(v)) for v in values]
        if self == Granularity.YEAR:
            return [pd.DateOffset(years=int(v)) for v in values]

        # Fixed units (predictable duration)
        if self == Granularity.WEEK:
            return pd.to_timedelta([v * 7 for v in values], unit="D")
        # DAY or HOUR
        return pd.to_timedelta(values, unit=self.pandas_freq)

    def truncate(self, dates):
        """
        Truncate dates to the start of their respective periods.

        Aligns timestamps to the beginning of the time unit defined
        by the granularity.
        """
        return pd.to_datetime(dates).dt.to_period(self.pandas_freq).dt.start_time

    @classmethod
    def infer_from_timedelta(cls, timedelta_series):
        """
        Infer the most appropriate granularity from a timedelta series.

        Analyzes the minimum non-zero component across all values to determine
        the finest necessary time unit. This ensures we don't lose precision.

        Args:
            timedelta_series: pandas Series of timedelta values

        Returns:
            Granularity: Inferred granularity enum (HOUR, DAY, WEEK, MONTH, or YEAR)
        """
        # Check if any value has sub-day components (hours, minutes, etc.)
        has_hours = any(
            td.components.hours > 0
            or td.components.minutes > 0
            or td.components.seconds > 0
            for td in timedelta_series
        )

        if has_hours:
            # If any value has hour-level precision, use HOUR
            return cls.HOUR

        # All values are whole days - check magnitude using median
        median_duration = timedelta_series.median()
        median_days = median_duration.days

        if median_days >= 365:
            # >= 1 year → YEAR
            return cls.YEAR
        if median_days >= 60:
            # >= ~2 months → MONTH
            return cls.MONTH
        if median_days >= 14:
            # >= 2 weeks → WEEK
            return cls.WEEK
        # < 2 weeks → DAY
        return cls.DAY

    @classmethod
    def infer_from_dateoffset(cls, dateoffset_series):
        """
        Infer the most appropriate granularity from a Series of DateOffset objects.

        Analyzes the offset types to determine the appropriate time unit.
        Checks kwds to identify the finest granularity present across all offsets.

        Args:
            dateoffset_series: pandas Series of pd.DateOffset objects

        Returns:
            Granularity: Inferred granularity enum

        Notes:
            - Uses finest granularity approach: checks for hours, then days/weeks, then months, then years
            - For mixed offsets (e.g., months + days), returns the finest unit present
        """
        # Collect all kwds keys from all offsets
        all_keys = set()
        for offset in dateoffset_series:
            all_keys.update(offset.kwds.keys())

        # Check for finest granularity first (finest to coarsest)
        if "hours" in all_keys or "minutes" in all_keys or "seconds" in all_keys:
            return cls.HOUR
        if "days" in all_keys or "weeks" in all_keys:
            # Could be DAY or WEEK, but DAY is safer (can represent weeks as multiples)
            return cls.DAY
        if "months" in all_keys:
            return cls.MONTH
        if "years" in all_keys:
            return cls.YEAR

        # Fallback: assume MONTH for calendar-based offsets
        return cls.MONTH

    @classmethod
    def infer(cls, duration_data):
        """
        Infer granularity from duration data (auto-detects type).

        Automatically detects whether the input is timedelta-based or DateOffset-based
        and calls the appropriate inference method.

        Args:
            duration_data: pandas Series of timedelta or DateOffset values

        Returns:
            Granularity: Inferred granularity enu

        Raises:
            ValueError: If duration_data is empty or type is not recognized
        """
        # Empty data - cannot infer
        if len(duration_data) == 0:
            raise ValueError("Cannot infer granularity from empty duration data")

        # Check first element type to determine approach
        first_elem = duration_data.iloc[0]

        # DateOffset → calendar-based (MONTH, YEAR)
        if isinstance(first_elem, pd.DateOffset):
            return cls.infer_from_dateoffset(duration_data)

        # Timedelta → fixed units (HOUR, DAY, WEEK)
        if isinstance(first_elem, pd.Timedelta):
            return cls.infer_from_timedelta(duration_data)

        # Unknown type
        raise ValueError(
            f"Cannot infer granularity from type {type(first_elem)}. "
            f"Expected timedelta or DateOffset, got {type(first_elem).__name__}."
        )
