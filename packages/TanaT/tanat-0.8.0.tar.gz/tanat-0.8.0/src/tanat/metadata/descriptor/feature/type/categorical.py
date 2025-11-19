#!/usr/bin/env python3
"""Categorical feature type implementation."""

from typing import Optional

import pandas as pd
from pydantic.dataclasses import dataclass
from pydantic import field_validator
from pypassist.fallback.typing import List
from pypassist.dataclass.decorators.viewer import viewer

from ..base import FeatureCoercer, FeatureSettingsBase


@viewer
@dataclass
class CategoricalFeatureSettings(FeatureSettingsBase):
    """
    Configuration settings for categorical feature type.

    Attributes:
        loader_type: Type of lazy loader (inherited from base)
        loader_kwargs: Loader configuration kwargs (inherited from base)
        categories: List of valid category values
        ordered: Whether categories have an ordering

    Note: `loader_type` and `loader_kwargs` are inherited from `FeatureSettingsBase`.
    """

    categories: Optional[List[str]] = None
    ordered: bool = False

    @field_validator("categories", mode="before")
    @classmethod
    def convert_categories_to_str(cls, v):
        """Convert all categories to strings (pd.Categorical behavior)."""
        if v is None:
            return None
        return [str(c) for c in v]

    def has_missing_required_fields(self):
        """Check if required fields are missing."""
        return not self.categories

    def complete_from_data(self, series):
        """Complete missing required fields from data.

        Only fills categories if empty. User values are preserved.

        Args:
            series: Pandas Series to analyze

        Returns:
            CategoricalFeatureSettings with completed fields
        """
        if not self.has_missing_required_fields():
            return self

        if isinstance(series.dtype, pd.CategoricalDtype):
            categories = series.cat.categories.tolist()
        else:
            unique_vals = series.dropna().unique()
            categories = sorted(str(v) for v in unique_vals)

        return CategoricalFeatureSettings(
            categories=categories,
            ordered=self.ordered,
            loader_type=self.loader_type,
            loader_kwargs=self.loader_kwargs,
        )


class CategoricalFeatureCoercer(FeatureCoercer, register_name="categorical"):
    """
    Coercer for categorical feature columns.
    """

    SETTINGS_DATACLASS = CategoricalFeatureSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = CategoricalFeatureSettings()
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype for this feature type."""
        return pd.CategoricalDtype(
            categories=self.settings.categories, ordered=self.settings.ordered
        )

    @staticmethod
    def _infer_settings(series):
        """Infer categorical settings from pandas Series.

        Args:
            series: Pandas Series with categorical data

        Returns:
            CategoricalFeatureSettings with inferred categories
        """
        if isinstance(series.dtype, pd.CategoricalDtype):
            return CategoricalFeatureSettings(
                categories=series.cat.categories.tolist(),
                ordered=series.cat.ordered,
            )

        unique_vals = series.dropna().unique()
        return CategoricalFeatureSettings(
            categories=sorted(str(v) for v in unique_vals),
            ordered=False,
        )

    def _coerce_immediate(self, series):
        """Coerce Series to categorical type.

        Args:
            series: Pandas Series to coerce

        Returns:
            Pandas Series with categorical dtype
        """
        result = series.astype(str)
        result = result.replace("nan", pd.NA)
        result = pd.Categorical(
            result,
            categories=self.settings.categories,
            ordered=self.settings.ordered,
        )
        return pd.Series(result, index=series.index)
