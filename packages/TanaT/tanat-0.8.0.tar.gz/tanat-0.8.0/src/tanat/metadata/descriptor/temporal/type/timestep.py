#!/usr/bin/env python3
"""Timestep temporal type implementation."""

from typing import Optional

import pandas as pd
from pandas.api.types import is_integer_dtype, is_float_dtype
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ....descriptor.temporal.base import TemporalCoercer
from ....exception import MetadataCoercionError


@viewer
@dataclass
class TimestepSettings:
    """
    Configuration settings for timestep (numeric) temporal type.

    Attributes:
        min_value: Minimum timestep value in the data (optional, inferred if not provided)
        max_value: Maximum timestep value in the data (optional, inferred if not provided)
        dtype: Target pandas dtype (e.g., 'int64', 'float32')
    """

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    dtype: str = "float32"

    def has_missing_required_fields(self):
        """Check if required fields are missing."""
        return self.min_value is None or self.max_value is None

    def complete_from_data(self, series):
        """
        Complete missing required fields from data.

        Only fills min/max if None. User values are preserved.

        Args:
            series: Pandas Series to analyze

        Returns:
            TimestepSettings with completed fields
        """
        if not self.has_missing_required_fields():
            return self

        converted = pd.to_numeric(series, errors="coerce")

        min_value = self.min_value if self.min_value is not None else converted.min()
        max_value = self.max_value if self.max_value is not None else converted.max()

        return TimestepSettings(
            min_value=min_value,
            max_value=max_value,
            dtype=self.dtype,
        )

    def is_compatible_with(self, other):
        """
        Check if this timestep settings is compatible with another.

        For timestep, we are lenient: different dtypes and ranges can coexist
        as long as both are numeric timesteps. This allows flexibility in
        trajectory composition.

        Args:
            other: Another TimestepSettings instance or None.

        Returns:
            True if compatible (always True for timestep if both exist).
        """
        if other is None:
            return False

        if not isinstance(other, TimestepSettings):
            return False

        # Timestep is lenient: different dtypes/ranges are OK
        # Both being numeric timestep is sufficient for compatibility
        return True


class TimestepCoercer(TemporalCoercer, register_name="timestep"):
    """
    Coercer for numeric timestep temporal columns.
    """

    SETTINGS_DATACLASS = TimestepSettings

    def __init__(self, settings):
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype string for this temporal type."""
        return self.settings.dtype

    @staticmethod
    def _infer_settings(series):
        """
        Infer timestep settings from pandas Series.

        Args:
            series: Pandas Series with numeric data

        Returns:
            TimestepSettings with inferred min/max and dtype
        """
        converted = TimestepCoercer._to_numeric(series)
        inferred_dtype = "int64" if is_integer_dtype(converted) else "float64"

        return TimestepSettings(
            min_value=converted.min(),
            max_value=converted.max(),
            dtype=inferred_dtype,
        )

    def coerce(self, series):
        """
        Coerce Series to numeric timestep.

        Args:
            series: Pandas Series to coerce

        Returns:
            Pandas Series with numeric dtype
        """
        result = self._to_numeric(series)

        # Cast to target dtype
        if self.settings.dtype:
            # For integer dtypes with NaN, use nullable integer types
            if "int" in self.settings.dtype.lower() and result.isna().any():
                nullable_dtype = self.settings.dtype.replace("int", "Int")
                result = result.astype(nullable_dtype)
            else:
                result = result.astype(self.settings.dtype)

        return result

    @staticmethod
    def _to_numeric(series):
        """
        Convert Series to numeric with error handling.

        Args:
            series: Input Series

        Returns:
            Numeric Series

        Raises:
            MetadataCoercionError: If conversion fails
        """
        if is_integer_dtype(series) or is_float_dtype(series):
            return series
        try:
            return pd.to_numeric(series, errors="raise")
        except (ValueError, TypeError) as e:
            raise MetadataCoercionError(
                f"Failed to coerce series to timestep: {e}"
            ) from e
