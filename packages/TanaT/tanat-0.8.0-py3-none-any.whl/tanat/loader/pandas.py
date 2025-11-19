#!/usr/bin/env python3
"""
Pandas extension for lazy loading of data.
"""

import numpy as np
import pandas as pd
from pandas.api.extensions import ExtensionDtype, ExtensionArray
from pandas.core.algorithms import take
from pypassist.mixin.cachable import Cachable

from .config import LoaderConfig


class LoaderDtype(ExtensionDtype):
    """Pandas extension dtype for loader-backed lazy values."""

    type = object
    name = "loader"

    def __init__(self, loader_type, target_dtype=None):
        ExtensionDtype.__init__(self)
        self.loader_type = loader_type
        self.target_dtype = target_dtype

    @property
    def kind(self):
        return "O"

    @classmethod
    def construct_array_type(cls):
        return LoaderArray

    def __repr__(self):
        return (
            f"LoaderDtype(loader_type={self.loader_type!r}, "
            f"target_dtype={self.target_dtype!r})"
        )

    def __eq__(self, other):
        return (
            isinstance(other, LoaderDtype)
            and self.loader_type == other.loader_type
            and self.target_dtype == other.target_dtype
        )

    def __hash__(self):
        return hash((self.loader_type, self.target_dtype))


class LoaderArray(ExtensionArray, Cachable):
    """ExtensionArray storing LoaderConfig objects for lazy loading.

    Items are automatically loaded on integer access (e.g., iloc[0]).
    Slice access returns a new LoaderArray (lazy).

    The coerce_fn callback ensures consistent coercion between
    lazy and immediate loading paths.
    """

    def __init__(self, values, loader_type, target_dtype=None, coerce_fn=None):
        ExtensionArray.__init__(self)
        Cachable.__init__(self)
        self.loader_type = loader_type
        self._data = self._data_as_array(values)
        self.target_dtype = target_dtype
        self.coerce_fn = coerce_fn

    @property
    def dtype(self):
        return LoaderDtype(self.loader_type, self.target_dtype)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        """Get item(s) - auto-loads on integer access, stays lazy on slice.

        Integer access (e.g., arr[0] or iloc[0]) triggers automatic loading.
        Slice access (e.g., arr[1:3]) returns a new LoaderArray (lazy).
        """
        if isinstance(item, (int, np.integer)):
            # Auto-load on direct item access
            return self._load_item(int(item))
        # Keep lazy for slices
        return type(self)(
            self._data[item], self.loader_type, self.target_dtype, self.coerce_fn
        )

    def __setitem__(self, key, value):
        """Set item(s) - converts value to LoaderConfig if needed."""
        if isinstance(value, LoaderConfig):
            self._data[key] = value
        elif value is None or pd.isna(value):
            self._data[key] = None
        else:
            self._data[key] = self._create_loader_config(str(value))

    @staticmethod
    def _lazy_token(config):
        """Generate hashable token from LoaderConfig for comparison."""
        if config is None or pd.isna(config):
            return (None,)
        settings = config.settings
        if isinstance(settings, dict):
            settings = tuple(sorted(settings.items()))
        return (config.ltype, settings)

    def _create_loader_config(self, settings_str):
        """Create LoaderConfig from string representation."""
        settings = self._parse_settings_from_string(settings_str)
        return LoaderConfig(ltype=self.loader_type, settings=settings)

    @Cachable.caching_method()
    def _load_item(self, index):
        """Load a single item (cached)."""
        cfg = self._data[index]
        if cfg is None or pd.isna(cfg):
            return None
        return cfg.get_loader().load()

    def load_item(self, index):
        """Explicitly load a single item.

        Args:
            index: Index of item to load

        Returns:
            Loaded value
        """
        return self._load_item(index)

    def load_iter(self):
        """Yield (idx, loaded_value) for all items."""
        for i in range(len(self)):
            yield i, self._load_item(i)

    def load_all(self):
        """Load all items and apply coercion.

        Uses the coerce_fn callback to ensure consistent coercion
        with immediate loading path.

        Returns:
            Series with loaded and coerced data
        """
        loaded = [self._load_item(i) for i in range(len(self._data))]
        series = pd.Series(loaded, dtype=object)
        return self.coerce_fn(series)

    def __array__(self, dtype=None, copy=None):
        """Convert to numpy array for display/operations."""
        return np.array([self._repr_item(x) for x in self._data], dtype=object)

    def _repr_item(self, item):
        """String representation of a LoaderConfig."""
        if item is None or pd.isna(item):
            return "NaN"
        s = str(item.settings)
        if len(s) > 32:
            s = s[:29] + "..."
        return f"<{self.loader_type}:{s}>"

    def isna(self):
        """Return boolean array indicating NA values."""
        return pd.isna(self._data)

    def take(self, indices, *, allow_fill=False, fill_value=None):
        """Take elements from array."""
        result = take(self._data, indices, allow_fill=allow_fill, fill_value=fill_value)
        return type(self)(result, self.loader_type, self.target_dtype, self.coerce_fn)

    def copy(self):
        """Return a copy of this array."""
        return type(self)(
            self._data.copy(), self.loader_type, self.target_dtype, self.coerce_fn
        )

    @classmethod
    def _concat_same_type(cls, to_concat):
        """Concatenate multiple arrays of this type."""
        if not to_concat:
            return cls([], None, None, None)
        first = to_concat[0]
        data = np.concatenate([arr._data for arr in to_concat])
        return cls(data, first.loader_type, first.target_dtype, first.coerce_fn)

    @classmethod
    def _from_sequence(cls, scalars, *, dtype=None, copy=False):
        """Construct from sequence."""
        if dtype is not None and isinstance(dtype, LoaderDtype):
            return cls(scalars, dtype.loader_type, dtype.target_dtype)
        return cls(scalars, None, None)

    @classmethod
    def _from_factorized(cls, values, original):
        """Reconstruct from factorized data."""
        return cls(
            values, original.loader_type, original.target_dtype, original.coerce_fn
        )

    def _data_as_array(self, values):
        """Convert input values to array of LoaderConfig objects."""
        out = []
        for v in values:
            if isinstance(v, LoaderConfig):
                out.append(v)
            elif v is None or pd.isna(v):
                out.append(None)
            else:
                out.append(self._create_loader_config(str(v)))
        return np.asarray(out, dtype=object)

    def _parse_settings_from_string(self, settings_str):
        """Parse settings dict from string representation."""
        parts = {}
        for part in settings_str.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                parts[k.strip()] = v.strip().strip("\"'")
        return parts

    def _reduce(self, name, *, skipna=True, **kwargs):
        """Support reduction operations by loading all data."""
        if name in ["sum", "mean", "std", "var", "min", "max"]:
            return getattr(self.load_all(), name)(skipna=skipna, **kwargs)
        return super()._reduce(name, skipna=skipna, **kwargs)

    def _values_for_argsort(self):
        """Return values for sorting."""
        return np.array([self._lazy_token(c) for c in self._data], dtype=object)

    def _values_for_factorize(self):
        """Return values and NA sentinel for factorization."""
        vals = np.array([self._lazy_token(c) for c in self._data], dtype=object)
        return vals, pd.NA

    def _accumulate(self, name, *, skipna=True, **kwargs):
        """Perform accumulation operation (cumsum, cumprod, etc.)."""
        loaded = self.load_all()
        return getattr(loaded, name)(skipna=skipna, **kwargs)

    def interpolate(
        self,
        *,
        method="linear",
        limit=None,
        limit_direction="forward",
        limit_area=None,
        copy=True,
        **kwargs,
    ):
        """Interpolate missing values."""
        loaded = self.load_all()
        return loaded.interpolate(
            method=method,
            limit=limit,
            limit_direction=limit_direction,
            limit_area=limit_area,
            **kwargs,
        )
