#!/usr/bin/env python3
"""Numerical feature type implementation."""

from typing import Optional

import pandas as pd
from pandas.api.types import is_integer_dtype
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ..base import FeatureCoercer, FeatureSettingsBase


@viewer
@dataclass
class NumericalFeatureSettings(FeatureSettingsBase):
    """
    Configuration settings for numerical feature type.

    Attributes:
        loader_type: Type of lazy loader (inherited from base)
        loader_kwargs: Loader configuration kwargs (inherited from base)
        dtype: Target pandas dtype (e.g., 'float32', 'int64')
        min_value: Minimum value in the data
        max_value: Maximum value in the data

    Note: `loader_type` and `loader_kwargs` are inherited from `FeatureSettingsBase`.
    """

    dtype: str = "Float32"
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def has_missing_required_fields(self):
        """Check if required fields are missing."""
        return self.min_value is None or self.max_value is None

    def complete_from_data(self, series):
        """Complete missing required fields from data.

        Only fills min/max if None. User values are preserved.

        Args:
            series: Pandas Series to analyze

        Returns:
            NumericalFeatureSettings with completed fields
        """
        if not self.has_missing_required_fields():
            return self

        converted = pd.to_numeric(series, errors="coerce")

        min_value = (
            self.min_value if self.min_value is not None else float(converted.min())
        )
        max_value = (
            self.max_value if self.max_value is not None else float(converted.max())
        )

        return NumericalFeatureSettings(
            min_value=min_value,
            max_value=max_value,
            dtype=self.dtype,
            loader_type=self.loader_type,
            loader_kwargs=self.loader_kwargs,
        )


class NumericalFeatureCoercer(FeatureCoercer, register_name="numerical"):
    """
    Coercer for numerical (int/float) feature columns.
    """

    SETTINGS_DATACLASS = NumericalFeatureSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = NumericalFeatureSettings()
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype string for this feature type."""
        return self.settings.dtype

    @staticmethod
    def _infer_settings(series):
        """Infer numerical settings from pandas Series.

        Args:
            series: Pandas Series with numeric data

        Returns:
            NumericalFeatureSettings with inferred dtype and min/max
        """
        converted = pd.to_numeric(series, errors="coerce")

        inferred_dtype = "Float32"  # type nullable
        if is_integer_dtype(series):
            inferred_dtype = "Int32" if series.max() < 2**31 else "Int64"

        return NumericalFeatureSettings(
            min_value=float(converted.min()),
            max_value=float(converted.max()),
            dtype=inferred_dtype,
        )

    def _coerce_immediate(self, series):
        """Coerce Series to numerical type.

        Args:
            series: Pandas Series to coerce

        Returns:
            Pandas Series with numeric dtype (handles NaN with nullable types)
        """
        result = pd.to_numeric(series, errors="raise")
        result = result.astype(self.settings.dtype)
        return result
