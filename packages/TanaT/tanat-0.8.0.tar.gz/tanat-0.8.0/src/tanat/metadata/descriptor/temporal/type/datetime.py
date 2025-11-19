#!/usr/bin/env python3
"""DateTime temporal type implementation."""

from typing import Optional

import pandas as pd
from pandas import Timestamp
from pandas.api.types import is_datetime64_any_dtype
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, field_validator
from pypassist.dataclass.decorators.viewer import viewer

from ....descriptor.temporal.base import TemporalCoercer
from ....exception import MetadataCoercionError


@viewer
@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class DateTimeSettings:
    """
    Configuration settings for datetime temporal type.

    Attributes:
        min_value: Minimum datetime value in the data (optional, inferred if not provided)
        max_value: Maximum datetime value in the data (optional, inferred if not provided)
        timezone: Timezone string (e.g., 'UTC', 'Europe/Paris')
        format: Optional datetime format string for parsing
    """

    min_value: Optional[Timestamp] = None
    max_value: Optional[Timestamp] = None
    timezone: Optional[str] = None
    format: Optional[str] = None

    @field_validator("min_value", "max_value", mode="before")
    @classmethod
    def _validate_timestamp(cls, value):
        """
        Convert string to Timestamp if needed.

        Accepts:
        - None → None (optional field)
        - pandas.Timestamp → unchanged
        - str → parsed (e.g., "2020-01-01", "2020-01-01T12:30:00")
        - datetime.datetime → converted
        - datetime.date → converted (time set to 00:00:00)
        - numpy.datetime64 → converted

        Args:
            value: Input value to validate/convert

        Returns:
            Timestamp or None
        """
        if value is None:
            return None

        if isinstance(value, Timestamp):
            return value

        # Try to convert using Timestamp constructor
        # It handles: str, datetime, date, numpy.datetime64, etc.
        try:
            return Timestamp(value)
        except Exception as e:
            raise ValueError(
                f"Cannot convert {type(value).__name__} '{value}' to Timestamp. "
                f"Expected: str, datetime, date, or Timestamp. Error: {e}"
            ) from e

    def has_missing_required_fields(self):
        """Check if required fields are missing."""
        return self.min_value is None or self.max_value is None

    def complete_from_data(self, series):
        """
        Complete missing required fields from data.

        Only fills min/max/timezone if None. User values are preserved.

        Args:
            series: Pandas Series to analyze

        Returns:
            DateTimeSettings with completed fields
        """
        if not self.has_missing_required_fields():
            return self

        converted = pd.to_datetime(series, errors="coerce")

        min_value = self.min_value if self.min_value is not None else converted.min()
        max_value = self.max_value if self.max_value is not None else converted.max()

        timezone = self.timezone
        if timezone is None and hasattr(converted.dt, "tz") and converted.dt.tz:
            timezone = getattr(converted.dt.tz, "zone", None)

        return DateTimeSettings(
            min_value=min_value,
            max_value=max_value,
            timezone=timezone,
            format=self.format,
        )

    def is_compatible_with(self, other):
        """
        Check if this datetime settings is compatible with another in trajectory composition.

        For datetime, compatibility means same format (critical for parsing).
        Other fields (min/max, timezone) can differ across sequences.

        Args:
            other: Another DateTimeSettings instance or None.

        Returns:
            True if compatible (i.e., same format).
        """
        if other is None:
            return False

        if not isinstance(other, DateTimeSettings):
            return False

        # Critical: format must match for parsing consistency
        return self.format == other.format


class DateTimeCoercer(TemporalCoercer, register_name="datetime"):
    """
    Coercer for datetime temporal columns.
    """

    SETTINGS_DATACLASS = DateTimeSettings

    def __init__(self, settings):
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype string for this temporal type."""
        if self.settings.timezone:
            return f"datetime64[ns, {self.settings.timezone}]"
        return "datetime64[ns]"

    @staticmethod
    def _infer_settings(series):
        """
        Infer datetime settings from pandas Series.

        Args:
            series: Pandas Series with datetime data

        Returns:
            DateTimeSettings with inferred min/max and timezone
        """
        converted = DateTimeCoercer._to_datetime(series)

        timezone = None
        if hasattr(converted.dt, "tz") and converted.dt.tz:
            timezone = getattr(converted.dt.tz, "zone", None)

        return DateTimeSettings(
            min_value=converted.min(),
            max_value=converted.max(),
            timezone=timezone,
        )

    def coerce(self, series):
        """
        Coerce Series to datetime with timezone handling.

        Args:
            series: Pandas Series to coerce

        Returns:
            Pandas Series with datetime64 dtype
        """
        result = self._to_datetime(series, date_format=self.settings.format)

        if self.settings.timezone and result.dt.tz is None:
            result = result.dt.tz_localize(self.settings.timezone)
        elif self.settings.timezone and str(result.dt.tz) != self.settings.timezone:
            result = result.dt.tz_convert(self.settings.timezone)

        return result

    @staticmethod
    def _to_datetime(series, date_format=None):
        """
        Convert Series to datetime with error handling.

        Args:
            series: Input Series
            date_format: Optional datetime format string

        Returns:
            Datetime Series

        Raises:
            MetadataCoercionError: If conversion fails
        """
        if is_datetime64_any_dtype(series) and date_format is None:
            return series

        try:
            if is_datetime64_any_dtype(series):
                series = series.dt.strftime(date_format)
            return pd.to_datetime(series, format=date_format, errors="raise")
        except (ValueError, TypeError) as e:
            format_info = f" with format '{date_format}'" if date_format else ""
            raise MetadataCoercionError(
                f"Failed to coerce series to datetime{format_info}: {e}"
            ) from e
