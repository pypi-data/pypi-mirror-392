#!/usr/bin/env python3
"""
Static feature settings for sequence objects.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pydantic import field_validator
from pypassist.fallback.typing import List


@dataclass
class StaticFeatureSettings:
    """
    Static feature configuration for sequence objects.

    Manages static features that remain constant across time for each
    sequence (demographics, categories, etc.). Optional configuration
    for sequences without static data.

    Attributes:
        static_features (Optional[List[str]]): Column names for static
            features. None if no static features are available.
    """

    static_features: Optional[List[str]] = None

    @field_validator("static_features", mode="before")
    @classmethod
    def normalize_static_features(cls, v):
        """
        Convert single string to list for user convenience.

        Allows users to pass a simple string when they have only one static
        feature, instead of requiring a list. Pydantic then handles all native
        validation (type checking, etc.).

        Args:
            v: Static feature(s) as string or list

        Returns:
            List: The value as a list (Pydantic will validate List[str] after)
        """
        if isinstance(v, str):
            return [v]
        return v
