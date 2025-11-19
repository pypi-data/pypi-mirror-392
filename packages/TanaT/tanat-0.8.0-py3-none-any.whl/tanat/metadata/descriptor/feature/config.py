#!/usr/bin/env python3
"""Feature descriptor configuration."""

from typing import Optional, Union

import pandas as pd
from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_datetime64_any_dtype,
    is_object_dtype,
    is_bool_dtype,
)
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.utils.typing import ParamDict

from .base import FeatureCoercer, FeatureSettingsBase
from ...exception import MetadataInferenceError


@registry(base_cls=FeatureCoercer, register_name_attr="feature_type")
@viewer
@dataclass
class FeatureDescriptor:
    """
    User-facing configuration for feature column type.

    This dataclass describes the desired feature type and its settings.
    Use get_descriptor() to obtain the actual coercer implementation.

    Attributes:
        feature_type: Type name ('numerical', 'categorical', or 'textual')
        settings: Type-specific configuration dict (optional)
    """

    feature_type: str
    settings: Optional[Union[ParamDict, FeatureSettingsBase]] = None

    @classmethod
    def infer(cls, series, type_hint=None):
        """
        Infer feature descriptor configuration from pandas Series.

        Detects feature type and computes settings. Type detection can be
        skipped by providing a type hint.

        Args:
            series: Pandas Series to analyze
            type_hint: Optional type hint ('categorical', 'numerical', 'textual')

        Returns:
            FeatureDescriptor with inferred type and settings

        Raises:
            MetadataInferenceError: If series is datetime type (not allowed for features)
        """
        feature_type = type_hint if type_hint else cls._detect_type(series)
        coercer_cls = FeatureCoercer.get_registered(feature_type)
        settings = coercer_cls._infer_settings(  # pylint: disable=protected-access
            series
        )

        return cls(feature_type=feature_type, settings=settings)

    @staticmethod
    def _detect_type(series):
        """
        Detect feature type from series data.

        Uses simple heuristics:
        - Timedelta or DateOffset → duration
        - Numeric dtype → numerical
        - Boolean/categorical dtype → categorical
        - String with low cardinality (<100) and short length (<50 chars avg) → categorical
        - Everything else → textual

        Args:
            series: Pandas Series to analyze

        Returns:
            'duration', 'numerical', 'categorical', or 'textual'

        Raises:
            MetadataInferenceError: If series is datetime (not valid for features)
        """
        # Reject datetime
        if is_datetime64_any_dtype(series):
            raise MetadataInferenceError(
                "Cannot infer feature from datetime series. Use temporal columns instead."
            )

        # Duration types (timedelta or DateOffset)
        if pd.api.types.is_timedelta64_dtype(series):
            return "duration"

        # Check for DateOffset in object series
        if is_object_dtype(series) and len(series) > 0:
            if isinstance(series.iloc[0], pd.DateOffset):
                return "duration"

        # Numeric types
        if is_integer_dtype(series) or is_float_dtype(series):
            return "numerical"

        # Boolean or pandas categorical dtype
        if is_bool_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            return "categorical"

        # Object/string types - analyze content
        if is_object_dtype(series):
            non_null = series.dropna()

            if len(non_null) == 0:
                return "textual"  # Default for empty

            # Convert to string for analysis
            str_series = non_null.astype(str)

            # Check cardinality and length
            unique_count = len(str_series.unique())
            avg_length = str_series.str.len().mean()

            # Categorical if low cardinality and short values
            if unique_count < 100 and avg_length < 50:
                return "categorical"

            return "textual"

        # Fallback to categorical
        return "categorical"

    def get_descriptor(self):
        """
        Instantiate the coercer implementation for this configuration.

        Returns:
            FeatureCoercer subclass instance (Numerical/Categorical/TextualFeatureCoercer)
        """
        descriptor_cls = FeatureCoercer.get_registered(self.feature_type)
        return descriptor_cls(settings=self.settings or {})
