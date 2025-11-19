#!/usr/bin/env python3
"""
Base settings for trajectory objects.
"""

from typing import Optional
import dataclasses

from pydantic.dataclasses import dataclass
from pydantic import model_validator

from ...sequence.settings.static_feature import StaticFeatureSettings
from ...sequence.settings.utils import _validate_no_column_conflicts


@dataclass
class BaseTrajectorySettings(StaticFeatureSettings):
    """
    Base settings for trajectory objects.

    Attributes:
        id_column: The name of the column representing the ID.
        static_features: The names of the columns representing the static features.
    """

    id_column: Optional[str] = None

    def reset_static_settings(self):
        """
        Reset static settings.

        Returns:
            A new instance with reset static settings.
        """
        return dataclasses.replace(self, id_column=None, static_features=None)

    @model_validator(mode="after")
    def validate_column_conflicts(self):
        """
        Validate column conflicts after initialization.

        Using Pydantic's @model_validator with mode='after' allows us to
        validate after all fields are set. Any ValueError raised here will
        be wrapped by Pydantic in a ValidationError with clear error details.

        Raises:
            ValueError: When column names conflict across settings.
        """
        _validate_no_column_conflicts(settings=self)
        return self
