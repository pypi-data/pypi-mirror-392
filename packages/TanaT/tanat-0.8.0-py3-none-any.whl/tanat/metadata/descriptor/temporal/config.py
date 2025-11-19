#!/usr/bin/env python3
"""Temporal descriptor configuration (user-facing)."""

from typing import Union, Optional

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_integer_dtype, is_float_dtype
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.utils.typing import ParamDict

from ....metadata.exception import MetadataInferenceError
from .base import TemporalCoercer
from .type.datetime import DateTimeSettings
from .type.timestep import TimestepSettings


@registry(base_cls=TemporalCoercer, register_name_attr="temporal_type")
@viewer
@dataclass
class TemporalDescriptor:
    """
    User-facing configuration for temporal column type.

    This dataclass describes the desired temporal type and its settings.
    Use get_descriptor() to obtain the actual coercer implementation.

    Attributes:
        temporal_type: Type name ('datetime' or 'timestep')
        settings: Type-specific configuration dict
    """

    temporal_type: str
    settings: Optional[Union[ParamDict, DateTimeSettings, TimestepSettings]] = None

    @classmethod
    def infer(cls, series, type_hint=None):
        """
        Infer temporal descriptor configuration from pandas Series.

        Detects temporal type and computes settings. Type detection can be
        skipped by providing a type hint.

        Args:
            series: Pandas Series to analyze
            type_hint: Optional type hint ('datetime' or 'timestep')

        Returns:
            TemporalDescriptor with inferred type and settings

        Raises:
            MetadataInferenceError: If series cannot be interpreted as temporal
        """
        temporal_type = type_hint if type_hint else cls._detect_type(series)
        coercer_cls = TemporalCoercer.get_registered(temporal_type)
        settings = coercer_cls._infer_settings(  # pylint: disable=protected-access
            series
        )

        return cls(temporal_type=temporal_type, settings=settings)

    @staticmethod
    def _detect_type(series):
        """
        Detect temporal type from series data.

        Args:
            series: Pandas Series to analyze

        Returns:
            'datetime' or 'timestep'

        Raises:
            MetadataInferenceError: If type cannot be determined
        """
        # Check if already datetime
        if is_datetime64_any_dtype(series):
            return "datetime"

        # Check if numeric (timestep)
        if is_integer_dtype(series) or is_float_dtype(series):
            return "timestep"

        # Try datetime parsing
        try:
            pd.to_datetime(series, errors="raise")
            return "datetime"
        except (ValueError, TypeError):
            pass

        # Try numeric parsing
        try:
            pd.to_numeric(series, errors="raise")
            return "timestep"
        except (ValueError, TypeError):
            pass

        raise MetadataInferenceError(
            f"Cannot infer temporal type from series with dtype {series.dtype}. "
            "Expected datetime-like or numeric data."
        )

    def get_descriptor(self):
        """
        Instantiate the coercer implementation for this configuration.

        Returns:
            TemporalCoercer subclass instance (DateTimeCoercer or TimestepCoercer)
        """
        descriptor_cls = TemporalCoercer.get_registered(self.temporal_type)
        return descriptor_cls(settings=self.settings or {})
