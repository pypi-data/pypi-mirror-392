#!/usr/bin/env python3
"""
Temporal metadata component.
"""

import logging

from typing import Optional
from pydantic.dataclasses import dataclass

from ..exception import MetadataValidationError
from ..descriptor.temporal.config import TemporalDescriptor
from ...time.granularity import Granularity

LOGGER = logging.getLogger(__name__)


@dataclass
class TemporalMetadata:
    """
    Temporal metadata component.

    Attributes:
        temporal_descriptor: Temporal descriptor configuration.
        granularity: Time granularity for temporal data.
    """

    temporal_descriptor: Optional[TemporalDescriptor] = None
    granularity: Optional[Granularity] = None

    def __post_init__(self):
        """Validate and initialize coercer cache."""
        self._validate_granularity_compatibility()
        self._coercer = None

    def _validate_granularity_compatibility(self):
        """
        Validate granularity compatibility with temporal descriptor.

        Automatically sets default granularity based on temporal type if not specified.

        Raises:
            MetadataValidationError: If granularity is incompatible with temporal type.
        """
        if self.temporal_descriptor is None:
            return

        descriptor_type = self.temporal_descriptor.temporal_type.lower()

        if descriptor_type == "timestep":
            self._validate_timestep_granularity()
        elif descriptor_type == "datetime":
            self._validate_datetime_granularity()

    def _validate_timestep_granularity(self):
        """
        Validate and set granularity for TIMESTEP type.

        Raises:
            MetadataValidationError: If granularity is not UNIT.
        """
        if self.granularity is None:
            self.granularity = Granularity.UNIT
            LOGGER.debug("Timestep granularity defaulted to UNIT")
            return

        if self.granularity != Granularity.UNIT:
            raise MetadataValidationError(
                f"TIMESTEP requires UNIT granularity, got {self.granularity}"
            )

    def _validate_datetime_granularity(self):
        """
        Validate and set granularity for DATETIME type.

        Raises:
            MetadataValidationError: If granularity is UNIT.
        """
        if self.granularity is None:
            self.granularity = Granularity.DAY
            LOGGER.debug("Granularity defaulted to DAY")
            return

        if self.granularity == Granularity.UNIT:
            raise MetadataValidationError(
                f"DATETIME requires time-based granularity, got {self.granularity.name}"
            )

    def is_complete(self):
        """
        Check if temporal metadata is complete.

        A temporal metadata is complete when:
        - descriptor is present
        - descriptor has settings
        - settings have all required fields
        - granularity is defined (for datetime type)

        Returns:
            bool: True if complete, False otherwise.
        """
        if not self._has_valid_descriptor():
            return False

        if not self._has_complete_settings():
            return False

        if not self._has_required_granularity():
            return False

        return True

    def _has_valid_descriptor(self):
        """
        Check if temporal descriptor exists.

        Returns:
            bool: True if descriptor is present.
        """
        if self.temporal_descriptor is None:
            LOGGER.debug("Temporal descriptor is missing")
            return False
        return True

    def _has_complete_settings(self):
        """
        Check if descriptor has complete settings.

        Returns:
            bool: True if settings are complete.
        """
        if self.temporal_descriptor.settings is None:
            LOGGER.debug("Temporal descriptor has no settings")
            return False

        if self.temporal_descriptor.settings.has_missing_required_fields():
            LOGGER.debug("Temporal descriptor has incomplete settings")
            return False

        return True

    def _has_required_granularity(self):
        """
        Check if required granularity is defined.

        Returns:
            bool: True if granularity requirement is met.
        """
        if self.temporal_descriptor.temporal_type == "datetime":
            if self.granularity is None:
                LOGGER.debug("Datetime temporal requires granularity")
                return False
        return True

    def coerce(self, series):
        """
        Coerce temporal column using cached coercer.

        Args:
            series: Pandas Series to coerce.

        Returns:
            pd.Series: Coerced Series with proper temporal type.

        Raises:
            ValueError: If no descriptor is available.
        """
        if self._coercer is None:
            self._coercer = self.temporal_descriptor.get_descriptor()

        return self._coercer.coerce(series)

    @classmethod
    def infer_from_dataframe(cls, df, temporal_columns, existing=None):
        """
        Infer temporal metadata from DataFrame.

        Applies 3-rule logic:
        1. Missing descriptor → full inference
        2. Descriptor without settings → infer with type hint
        3. Incomplete settings → complete from data

        Args:
            df: DataFrame containing temporal columns.
            temporal_columns: List of temporal column names.
            existing: Optional existing TemporalMetadata to complete.

        Returns:
            TemporalMetadata: Instance with inferred/completed descriptor.
        """
        existing_descriptor = existing.temporal_descriptor if existing else None
        existing_granularity = existing.granularity if existing else None

        # Infer descriptor
        descriptor = cls._infer_descriptor(df, temporal_columns, existing_descriptor)

        # Infer granularity
        granularity = cls._infer_granularity(existing_granularity, descriptor)

        return cls(temporal_descriptor=descriptor, granularity=granularity)

    @classmethod
    def _infer_descriptor(cls, df, temporal_columns, existing_descriptor):
        """
        Infer or complete temporal descriptor.

        Args:
            df: DataFrame containing temporal data.
            temporal_columns: List of temporal column names.
            existing_descriptor: Optional existing descriptor.

        Returns:
            TemporalDescriptor: Inferred or completed descriptor.
        """
        temporal_col = cls._get_first_temporal_column(df, temporal_columns)

        if existing_descriptor is None:
            # Rule 1: Missing descriptor → full inference
            return cls._infer_new_descriptor(df, temporal_col)

        # Rule 2 & 3: Complete existing descriptor
        return cls._complete_existing_descriptor(df, temporal_col, existing_descriptor)

    @classmethod
    def _get_first_temporal_column(cls, df, temporal_columns):
        """
        Get the first valid temporal column.

        Args:
            df: DataFrame.
            temporal_columns: List of temporal column names.

        Returns:
            str or None: First column name that exists in df, or None.
        """
        if not temporal_columns:
            return None

        temporal_col = temporal_columns[0]
        return temporal_col if temporal_col in df.columns else None

    @classmethod
    def _infer_new_descriptor(cls, df, temporal_col):
        """
        Infer a new descriptor from data.

        Args:
            df: DataFrame.
            temporal_col: Temporal column name.

        Returns:
            TemporalDescriptor or None: Inferred descriptor.
        """
        if temporal_col is None:
            return None

        descriptor = TemporalDescriptor.infer(df[temporal_col])
        LOGGER.debug("Inferred temporal descriptor from data")
        return descriptor

    @classmethod
    def _complete_existing_descriptor(cls, df, temporal_col, existing_descriptor):
        """
        Complete an existing descriptor using data.

        Args:
            df: DataFrame.
            temporal_col: Temporal column name.
            existing_descriptor: Existing descriptor to complete.

        Returns:
            TemporalDescriptor: Completed descriptor.
        """
        if existing_descriptor.settings is None:
            # Rule 2: Type hint only → infer with hint
            return cls._complete_with_type_hint(df, temporal_col, existing_descriptor)

        if existing_descriptor.settings.has_missing_required_fields():
            # Rule 3: Incomplete settings → complete
            return cls._complete_settings(df, temporal_col, existing_descriptor)

        # Already complete
        return existing_descriptor

    @classmethod
    def _complete_with_type_hint(cls, df, temporal_col, existing_descriptor):
        """
        Complete descriptor using type hint.

        Args:
            df: DataFrame.
            temporal_col: Temporal column name.
            existing_descriptor: Existing descriptor with type hint.

        Returns:
            TemporalDescriptor: Completed descriptor.
        """
        if temporal_col is None:
            return existing_descriptor

        descriptor = TemporalDescriptor.infer(
            df[temporal_col], type_hint=existing_descriptor.temporal_type
        )
        LOGGER.debug("Completed temporal descriptor with type hint")
        return descriptor

    @classmethod
    def _complete_settings(cls, df, temporal_col, existing_descriptor):
        """
        Complete descriptor settings from data.

        Args:
            df: DataFrame.
            temporal_col: Temporal column name.
            existing_descriptor: Existing descriptor with incomplete settings.

        Returns:
            TemporalDescriptor: Descriptor with completed settings.
        """
        if temporal_col is None:
            return existing_descriptor

        completed_settings = existing_descriptor.settings.complete_from_data(
            df[temporal_col]
        )
        descriptor = type(existing_descriptor)(
            temporal_type=existing_descriptor.temporal_type,
            settings=completed_settings,
        )
        LOGGER.debug("Completed temporal descriptor settings")
        return descriptor

    @classmethod
    def _infer_granularity(cls, existing_granularity, descriptor):
        """
        Infer granularity if needed.

        Args:
            existing_granularity: Existing granularity value.
            descriptor: Temporal descriptor.

        Returns:
            Granularity or None: Inferred or existing granularity.
        """
        if existing_granularity is not None:
            return existing_granularity

        if descriptor is None:
            return None

        if descriptor.temporal_type == "datetime":
            LOGGER.debug("Granularity set to: DAY")
            return Granularity.DAY

        return None

    def describe(self, verbose=False):
        """
        Human-readable description of temporal metadata.

        Args:
            verbose: If True, include descriptor details.

        Returns:
            str: Formatted string describing the temporal metadata.
        """
        lines = ["Temporal:"]

        if self.temporal_descriptor:
            lines.extend(self._describe_configuration(verbose))
        else:
            lines.append("  (none)")

        return "\n".join(lines)

    def _describe_configuration(self, verbose):
        """
        Generate description lines for temporal configuration.

        Args:
            verbose: If True, include detailed settings.

        Returns:
            list: Description lines.
        """
        lines = [
            f"  Type: {self.temporal_descriptor.temporal_type}",
            f"  Granularity: {self.granularity}",
        ]

        if verbose and self.temporal_descriptor.settings:
            lines.append(f"  Settings: {self.temporal_descriptor.settings}")

        return lines
