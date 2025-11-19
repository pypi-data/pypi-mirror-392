#!/usr/bin/env python3
"""Textual feature type implementation."""

from typing import Optional

import pandas as pd
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ..base import FeatureCoercer, FeatureSettingsBase


@viewer
@dataclass
class TextualFeatureSettings(FeatureSettingsBase):
    """
    Configuration settings for textual feature type.

    Attributes:
        loader_type: Type of lazy loader (inherited from base)
        loader_kwargs: Loader configuration kwargs (inherited from base)
        max_length: Maximum text length in the data

    Note: `loader_type` and `loader_kwargs` are inherited from `FeatureSettingsBase`.
    """

    max_length: Optional[int] = None

    def has_missing_required_fields(self):
        """Check if required fields are missing."""
        return False

    def complete_from_data(self, series):  # pylint: disable=unused-argument
        """Complete missing required fields from data.

        Textual settings have no required fields.

        Args:
            series: Pandas Series to analyze

        Returns:
            Self (unchanged)
        """
        return self


class TextualFeatureCoercer(FeatureCoercer, register_name="textual"):
    """Coercer for textual (string) feature columns.

    Handles free-form text data, typically with high cardinality.
    """

    SETTINGS_DATACLASS = TextualFeatureSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = TextualFeatureSettings()
        super().__init__(settings=settings)

    @property
    def pandas_dtype(self):
        """Return pandas dtype string for this feature type."""
        return "string"

    @staticmethod
    def _infer_settings(series):
        """Infer textual settings from pandas Series.

        Args:
            series: Pandas Series with text data

        Returns:
            TextualFeatureSettings with inferred max_length
        """
        str_series = series.astype(str)
        max_len = str_series.str.len().max()

        return TextualFeatureSettings(
            max_length=int(max_len),
        )

    def _coerce_immediate(self, series):
        """Coerce Series to textual (string) type.

        Args:
            series: Pandas Series to coerce

        Returns:
            Pandas Series with object dtype (strings with pd.NA for missing)
        """
        result = series.astype(str)
        result = result.replace("nan", pd.NA)
        return result
