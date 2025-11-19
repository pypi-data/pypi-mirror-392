#!/usr/bin/env python3
"""Duration feature type implementation."""

from typing import Optional, Union

import pandas as pd
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ..base import FeatureCoercer, FeatureSettingsBase
from .....time.granularity import Granularity


@viewer
@dataclass(config={"arbitrary_types_allowed": True})
class DurationFeatureSettings(FeatureSettingsBase):
    """
    Configuration settings for duration feature type.

    Durations represent time intervals that can be used in temporal operations.
    They can be specified as numeric values with a granularity unit, or as
    timedelta objects that will be inferred to a granularity.

    Attributes:
        loader_type: Type of lazy loader (inherited from base)
        loader_kwargs: Loader configuration kwargs (inherited from base)
        granularity: Time unit for duration values (HOUR, DAY, WEEK, MONTH, YEAR).
                    Allows conversion between numeric and timedelta/DateOffset representations.
        min_value: Minimum duration value (numeric for explicit granularity,
                   timedelta for inferred from timedelta data)
        max_value: Maximum duration value (numeric for explicit granularity,
                   timedelta for inferred from timedelta data)

    Examples:
        >>> # Numeric durations in hours (medication duration)
        >>> DurationFeatureSettings(granularity='HOUR', min_value=1, max_value=168)

        >>> # Numeric durations in days (hospital stay length)
        >>> DurationFeatureSettings(granularity='DAY', min_value=1, max_value=30)

        >>> # Default granularity (DAY)
        >>> DurationFeatureSettings()  # granularity='DAY' by default

        >>> # Timedelta series - granularity inferred from data
        >>> # pd.Series([timedelta(hours=6), timedelta(hours=24)]) → infers HOUR
        >>> # pd.Series([timedelta(days=1), timedelta(days=7)]) → infers DAY
    """

    granularity: Optional[Granularity] = None

    min_value: Optional[Union[float, pd.Timedelta]] = None
    max_value: Optional[Union[float, pd.Timedelta]] = None

    def has_missing_required_fields(self):
        """
        Check if required fields are missing.
        """
        return self.min_value is None or self.max_value is None

    def complete_from_data(self, series):
        """
        Complete missing fields from data.

        Infers min/max and potentially granularity from duration data.
        Supports both timedelta and DateOffset types.

        Args:
            series: Pandas Series containing durations (timedelta or DateOffset)

        Returns:
            DurationFeatureSettings with completed fields
        """
        # If all fields already set, return as-is
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.granularity is not None
        ):
            return self

        if series.isna().all():
            # All values are NaT - cannot infer anything
            return DurationFeatureSettings()

        # Detect if series contains timedelta
        if pd.api.types.is_timedelta64_dtype(series):
            # Infer granularity from timedelta values
            inferred_granularity = Granularity.infer_from_timedelta(series)
            min_val = series.min() if self.min_value is None else self.min_value
            max_val = series.max() if self.max_value is None else self.max_value

            return DurationFeatureSettings(
                granularity=inferred_granularity,
                min_value=min_val,
                max_value=max_val,
                loader_type=self.loader_type,
                loader_kwargs=self.loader_kwargs,
            )

        # Check if series contains DateOffset (calendar-based durations)
        if len(series) > 0 and isinstance(series.iloc[0], pd.DateOffset):
            # Infer granularity from DateOffset
            inferred_granularity = Granularity.infer_from_dateoffset(series)
            # For DateOffset, min/max are not directly comparable
            # Store the actual offset objects
            min_val = series.iloc[0] if self.min_value is None else self.min_value
            max_val = series.iloc[-1] if self.max_value is None else self.max_value

            return DurationFeatureSettings(
                granularity=inferred_granularity,
                min_value=min_val,
                max_value=max_val,
                loader_type=self.loader_type,
                loader_kwargs=self.loader_kwargs,
            )

        # Numeric values - infer min/max, keep existing granularity
        numeric_series = pd.to_numeric(series, errors="coerce")
        min_val = (
            self.min_value
            if self.min_value is not None
            else float(numeric_series.min())
        )
        max_val = (
            self.max_value
            if self.max_value is not None
            else float(numeric_series.max())
        )

        return DurationFeatureSettings(
            granularity=self.granularity,  # Keep existing or default
            min_value=min_val,
            max_value=max_val,
            loader_type=self.loader_type,
            loader_kwargs=self.loader_kwargs,
        )


class DurationFeatureCoercer(FeatureCoercer, register_name="duration"):
    """
    Coercer for duration feature columns.

    Converts duration values to timedelta or offset objects based on settings:
    - Numeric values + granularity → timedelta/DateOffset via Granularity.to_offsets()
    - Numeric values + unit → timedelta via pd.to_timedelta()
    - String values → timedelta via pd.to_timedelta()
    - timedelta values → preserved as-is

    The coercer is granularity-aware and can handle both fixed (HOUR, DAY, WEEK)
    and calendar-based (MONTH, YEAR) durations.
    """

    SETTINGS_DATACLASS = DurationFeatureSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = DurationFeatureSettings()
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype for duration type."""
        return "timedelta64[ns]"

    @staticmethod
    def _infer_settings(series):
        """
        Infer duration settings from pandas Series.

        Supports timedelta, DateOffset, and numeric series.

        Args:
            series: Pandas Series containing duration values

        Returns:
            DurationFeatureSettings with inferred granularity and min/max
        """
        # Detect if series contains timedelta
        if pd.api.types.is_timedelta64_dtype(series):
            # Infer appropriate granularity from values using Granularity method
            granularity = Granularity.infer_from_timedelta(series)
            return DurationFeatureSettings(
                granularity=granularity,
                min_value=series.min(),
                max_value=series.max(),
            )

        # Detect if series contains DateOffset (check first element)
        if len(series) > 0 and isinstance(series.iloc[0], pd.DateOffset):
            granularity = Granularity.infer_from_dateoffset(series)
            return DurationFeatureSettings(
                granularity=granularity,
                min_value=series.iloc[0],
                max_value=series.iloc[-1],
            )

        # Numeric values - default to HOUR granularity
        if pd.api.types.is_numeric_dtype(series):
            numeric_series = pd.to_numeric(series, errors="coerce")
            return DurationFeatureSettings(
                granularity=Granularity.HOUR,
                min_value=float(numeric_series.min()),
                max_value=float(numeric_series.max()),
            )

        # Try to parse as timedelta strings (e.g., "1 day", "3h", "30 minutes")
        try:
            converted = pd.to_timedelta(series, errors="raise")
            granularity = Granularity.infer_from_timedelta(converted)
            return DurationFeatureSettings(
                granularity=granularity,
                min_value=converted.min(),
                max_value=converted.max(),
            )
        except (ValueError, TypeError) as e:
            # Cannot parse as duration - raise clear error
            sample = series.iloc[0] if len(series) > 0 else "empty"
            raise ValueError(
                f"Cannot infer duration from series. "
                f"Expected numeric values, timedelta objects, DateOffset objects, "
                f"or parsable duration strings (e.g., '1 day', '3h'). "
                f"Got type '{type(sample).__name__}' with value: {sample}"
            ) from e

    def _coerce_immediate(self, series):
        """
        Coerce series to duration representation.

        Converts various input formats to pandas-compatible duration objects
        (timedelta or DateOffset).

        Args:
            series: Series containing duration values (numeric, string, or timedelta)

        Returns:
            Series with coerced duration values
        """
        # Case 0: All isna - return as-is
        if series.isna().all():
            return series

        # Case 1: Already timedelta - preserve
        if pd.api.types.is_timedelta64_dtype(series):
            return series

        # Case 2: Already DateOffset - preserve
        if len(series) > 0 and isinstance(series.iloc[0], pd.DateOffset):
            return series

        # Case 3: Numeric with granularity - use Granularity.to_offsets()
        # granularity is now a Granularity enum, not a string
        numeric_series = pd.to_numeric(series, errors="coerce")
        offsets = self.settings.granularity.to_offsets(numeric_series.values)

        # to_offsets returns list for calendar-based, Series for fixed
        if isinstance(offsets, list):
            # Calendar-based (MONTH, YEAR) - keep as list of DateOffset
            # Note: Can't store DateOffset in Series directly, convert to timedelta approximation
            # For proper handling, should be applied to timestamps directly
            return pd.Series(offsets, index=series.index)
        else:
            # Fixed units - already a Series of Timedelta
            return offsets
