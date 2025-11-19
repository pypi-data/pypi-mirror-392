#!/usr/bin/env python3
"""Feature coercer base class for numerical, categorical, and textual types."""

from typing import Optional
from abc import abstractmethod

import pandas as pd
from pydantic.dataclasses import dataclass
from pypassist.fallback.typing import Dict

from ..base import Coercer
from ...exception import MetadataCoercionError
from ....loader.config import LoaderConfig
from ....loader.pandas import LoaderArray
from ....utils.misc import string_to_dict


@dataclass
class FeatureSettingsBase:
    """
    Base settings for all feature coercers.

    Attributes:
        loader_type: Optional lazy loader type (e.g., 'txt', 'image')
        loader_kwargs: Configuration kwargs passed to the loader
    """

    loader_type: Optional[str] = None
    loader_kwargs: Optional[Dict] = None


class FeatureCoercer(Coercer):
    """
    Base class for feature column coercers.
    Supports lazy loading via LoaderConfig objects when loader_type is configured.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"

    @property
    def loader_type(self):
        """Loader type for lazy loading."""
        return getattr(self.settings, "loader_type", None)

    @property
    def loader_kwargs(self):
        """Loader kwargs for lazy loading."""
        return getattr(self.settings, "loader_kwargs", None)

    def coerce(self, series):
        """Coerce series with optional lazy loading.

        If loader_type is configured, series is expected to contain
        LoaderConfig objects (or dicts) for lazy loading.
        Otherwise, performs immediate coercion.

        Args:
            series: Series to coerce

        Returns:
            Coerced series (LoaderArray if lazy, regular Series if immediate)
        """
        if self.loader_type is not None:
            return self._coerce_with_loader(series)
        return self._coerce_immediate(series)

    def _coerce_with_loader(self, series):
        """Validate and preserve LoaderConfig objects for lazy loading.

        Args:
            series: Series containing LoaderConfig objects, dicts or strings

        Returns:
            LoaderArray with validated LoaderConfig objects
        """
        configs = []
        for value in series:
            if pd.isna(value):
                configs.append(None)
                continue

            if isinstance(value, LoaderConfig):
                if value.ltype != self.loader_type:
                    raise MetadataCoercionError(
                        f"Expected loader type '{self.loader_type}', got '{value.ltype}'"
                    )
                configs.append(value)
                continue

            # Support dict or string representation of LoaderConfig
            settings = string_to_dict(value) if isinstance(value, str) else value
            if not isinstance(settings, dict):
                raise MetadataCoercionError(
                    f"Expected LoaderConfig, dict or string, got {type(value)}"
                )

            configs.append(
                LoaderConfig(
                    ltype=self.loader_type, settings=settings.get("settings", settings)
                )
            )

        return LoaderArray(
            configs,
            loader_type=self.loader_type,
            target_dtype=self.pandas_dtype,
            coerce_fn=self._coerce_immediate,
        )

    @abstractmethod
    def _coerce_immediate(self, series):
        """Immediate coercion (no lazy loading).

        Subclasses implement their specific coercion logic here.

        Args:
            series: Series with actual values

        Returns:
            Coerced series
        """

    @property
    @abstractmethod
    def pandas_dtype(self):
        """
        Return pandas dtype for this feature type.
        """
