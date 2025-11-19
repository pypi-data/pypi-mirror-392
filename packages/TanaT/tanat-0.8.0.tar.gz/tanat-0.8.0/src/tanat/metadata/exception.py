#!/usr/bin/env python3
"""
Exceptions for metadata operations.
"""


class MetadataError(Exception):
    """Base error for metadata operations."""


class MetadataInferenceError(MetadataError):
    """Failed to infer metadata from data."""


class MetadataValidationError(MetadataError):
    """Metadata configuration is invalid."""


class MetadataCoercionError(MetadataError):
    """Failed to coerce data with given metadata."""


class TemporalIncoherenceError(MetadataValidationError):
    """
    Sequences in a trajectory have incompatible temporal configurations.

    All sequences in a trajectory must share:
    - Same temporal type (datetime vs timestep)
    - Same granularity
    - Same temporal settings (e.g., datetime format)
    """
