#!/usr/bin/env python3
"""Temporal coercer base class for datetime and timestep types."""

from ..base import Coercer


class TemporalCoercer(Coercer):
    """
    Base class for temporal column coercers.

    Temporal coercers handle time-related columns that define the temporal
    dimension of sequence data. Two types are supported:
    - DateTimeCoercer: For datetime64 data with timezone support
    - TimestepCoercer: For numeric timesteps (sequential integers/floats)
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"

    @property
    def min_value(self):
        """Minimum temporal value in the data."""
        return getattr(self.settings, "min_value", None)

    @property
    def max_value(self):
        """Maximum temporal value in the data."""
        return getattr(self.settings, "max_value", None)
