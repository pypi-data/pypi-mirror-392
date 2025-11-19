#!/usr/bin/env python3
"""
Base metadata mixin.
"""

from abc import ABC, abstractmethod
import dataclasses


class MetadataMixin(ABC):
    """
    Abstract base mixin for metadata management.
    """

    def __init__(self, metadata=None):
        """
        Initialize metadata with eager completion.

        Args:
            metadata: Optional metadata (None, dict, or Metadata instance).
        """
        validated = self._validate_metadata(metadata)
        self._metadata = self._infer_metadata(validated)

    @property
    def metadata(self):
        """Get complete metadata."""
        return self._metadata

    @property
    def granularity(self):
        """Get temporal granularity."""
        return self.metadata.granularity

    @granularity.setter
    def granularity(self, value):
        """Set temporal granularity."""
        self._set_granularity(value)

    @abstractmethod
    def _validate_metadata(self, metadata):
        """
        Validate and normalize input metadata.

        Args:
            metadata: None, dict, or Metadata instance.

        Returns:
            Normalized metadata instance or None.

        Raises:
            ValueError: If metadata format is invalid.
        """

    @abstractmethod
    def _infer_metadata(self, metadata):
        """
        Infer complete metadata from data.

        Args:
            metadata: Optional existing metadata to complete.

        Returns:
            Complete metadata instance.
        """

    @abstractmethod
    def _set_granularity(self, value):
        """
        Set granularity with validation.

        Args:
            value: Granularity value (string or Granularity enum).
        """

    @staticmethod
    def _validate_settings_type(settings, param_name="settings"):
        """
        Validate that settings is either a dict or a dataclass.

        Args:
            settings: Settings to validate.
            param_name: Name of the parameter (for error message).

        Raises:
            TypeError: If settings is not dict or dataclass.
        """
        if settings is None:
            return

        if isinstance(settings, dict):
            return

        if dataclasses.is_dataclass(settings):
            return

        raise TypeError(
            f"'{param_name}' must be a dict or dataclass, got {type(settings).__name__}"
        )

    @staticmethod
    def _settings_to_dict(settings):
        """
        Convert settings to dict if it's a dataclass, otherwise return as-is.

        Args:
            settings: Settings object (dict or dataclass) or None.

        Returns:
            dict or None: Settings as dict or None.
        """
        if settings is None:
            return {}

        if isinstance(settings, dict):
            return settings

        if dataclasses.is_dataclass(settings):
            return dataclasses.asdict(settings)

        return {}

    def _update_descriptor(
        self,
        current_descriptor,
        type_param_name,
        new_type=None,
        settings=None,
        **kwargs,
    ):
        """
        Generic helper to update any descriptor (temporal, entity, or static).

        Handles the common pattern of:
        1. Validating settings type
        2. Converting descriptor to dict
        3. Determining target type
        4. Resetting settings if type changed
        5. Merging settings with priority: current < settings param < kwargs

        Args:
            current_descriptor: Current descriptor (TemporalDescriptor or FeatureDescriptor).
            type_param_name: Name of the type field ('temporal_type' or 'feature_type').
            new_type: Optional new type value (e.g., "datetime", "categorical").
            settings: Optional settings dict or dataclass (overridden by kwargs).
            **kwargs: Individual settings to merge (highest priority).

        Returns:
            dict: Updated descriptor as dict, ready to be assigned to metadata.

        Raises:
            TypeError: If settings is not dict or dataclass.
        """
        # Validate settings type
        self._validate_settings_type(settings, "settings")

        # Convert current descriptor to dict
        descriptor_dict = dataclasses.asdict(current_descriptor)

        # Determine target type
        target_type = new_type or descriptor_dict[type_param_name]

        # Reset settings if type changed
        if new_type and new_type != descriptor_dict[type_param_name]:
            descriptor_dict["settings"] = {}

        descriptor_dict[type_param_name] = target_type

        # Merge settings: current < settings param < kwargs
        settings_dict = descriptor_dict.get("settings") or {}
        settings_dict.update(self._settings_to_dict(settings))
        settings_dict.update(kwargs)

        descriptor_dict["settings"] = settings_dict if settings_dict else None

        return descriptor_dict
