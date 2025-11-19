#!/usr/bin/env python3
"""Base coercer class."""

from abc import ABC, abstractmethod

from pydantic_core import core_schema
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable


class Coercer(ABC, Registrable, SettingsMixin):
    """
    Abstract base class for column type coercers.
    """

    def __init__(self, settings):
        """
        Initialize coercer with settings.

        Args:
            settings: Configuration dataclass for this type
        """
        SettingsMixin.__init__(self, settings)

    @abstractmethod
    def coerce(self, series):
        """
        Coerce Series to this coercer's target type.

        Args:
            series: Pandas Series to convert

        Returns:
            Coerced pandas Series with target dtype
        """

    @property
    @abstractmethod
    def pandas_dtype(self):
        """Target pandas dtype for this coercer."""

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """Allow Pydantic to validate Coercer instances."""
        return core_schema.any_schema()
