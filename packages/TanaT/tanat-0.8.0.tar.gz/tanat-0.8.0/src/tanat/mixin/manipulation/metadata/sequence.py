#!/usr/bin/env python3
"""
Sequence metadata mixin.
"""

import dataclasses

from ....metadata.sequence import SequenceMetadata
from ....time.granularity import Granularity
from .base import MetadataMixin


class SequenceMetadataMixin(MetadataMixin):
    """
    Metadata mixin for sequence containers.
    """

    def _validate_metadata(self, metadata):
        """
        Validate and normalize input metadata.

        Args:
            metadata: None, dict, or SequenceMetadata instance.

        Returns:
            SequenceMetadata instance or None.

        Raises:
            ValueError: If metadata format is invalid.
        """
        if metadata is None:
            return None
        if isinstance(metadata, dict):
            return SequenceMetadata(**metadata)
        if isinstance(metadata, SequenceMetadata):
            return metadata
        raise ValueError("Metadata must be a dict or SequenceMetadata instance.")

    def _infer_metadata(self, metadata):
        """
        Infer complete metadata from sequence data.

        Args:
            metadata: Optional existing metadata to complete.

        Returns:
            Complete SequenceMetadata instance.
        """
        return SequenceMetadata.from_sequence(sequence=self, metadata=metadata)

    def _set_granularity(self, value):
        """
        Set granularity for sequence metadata.

        Args:
            value: Granularity value (string or Granularity enum).
        """
        granularity = Granularity.from_str(value)
        self._metadata = dataclasses.replace(self.metadata, granularity=granularity)

    def _prepare_sequence_dataframe(self, df):
        """
        Prepare DataFrame with metadata coercion.

        Args:
            df: Raw DataFrame to prepare.

        Returns:
            Prepared DataFrame with coerced types.
        """
        return self._metadata.prepare_sequence_data(df, self.settings)

    def update_temporal_metadata(
        self, temporal_type=None, granularity=None, settings=None, **kwargs
    ):
        """
        Update temporal metadata.
        Systematically triggers cache clearing.

        Args:
            temporal_type: Optional new temporal type ("datetime" or "timestep").
            granularity: Optional new granularity (string or Granularity enum).
            settings: Optional new settings (dict or dataclass, overridden by kwargs).
            **kwargs: Individual settings fields to update (highest priority).

        Returns:
            self for chaining.

        Raises:
            TypeError: If settings is not dict or dataclass.

        Examples:
            >>> seq.update_temporal_metadata(temporal_type="datetime")
            >>> seq.update_temporal_metadata(format="%Y-%m-%d", timezone="UTC")
            >>> seq.update_temporal_metadata(granularity="HOUR")
        """
        # Use generic helper to update descriptor
        descriptor_dict = self._update_descriptor(
            current_descriptor=self.metadata.temporal_descriptor,
            type_param_name="temporal_type",
            new_type=temporal_type,
            settings=settings,
            **kwargs,
        )

        # Update metadata
        self._metadata = dataclasses.replace(
            self.metadata,
            temporal_descriptor=descriptor_dict,
            granularity=(
                granularity if granularity is not None else self.metadata.granularity
            ),
        )

        self.clear_cache()
        return self

    def update_entity_metadata(
        self, feature_name, feature_type=None, settings=None, **kwargs
    ):
        """
        Update entity metadata for a specific feature.
        Systematically triggers cache clearing.

        Args:
            feature_name: Name of the entity feature to update.
            feature_type: Optional new feature type (categorical/numerical/textual).
            settings: Optional new settings (dict or dataclass, overridden by kwargs).
            **kwargs: Individual settings fields to update (highest priority).

        Returns:
            self for chaining.

        Raises:
            ValueError: If feature not found in entity metadata.
            TypeError: If settings is not dict or dataclass.

        Examples:
            >>> seq.update_entity_metadata("age", feature_type="numerical")
            >>> seq.update_entity_metadata("category", categories=["A", "B"], ordered=True)
        """
        if feature_name not in self.metadata.entity_descriptors:
            raise ValueError(f"Feature '{feature_name}' not found in entity metadata.")

        descriptors = self.metadata.entity_descriptors.copy()

        # Use generic helper to update descriptor
        descriptors[feature_name] = self._update_descriptor(
            current_descriptor=descriptors[feature_name],
            type_param_name="feature_type",
            new_type=feature_type,
            settings=settings,
            **kwargs,
        )

        # Update metadata
        self._metadata = dataclasses.replace(
            self.metadata, entity_descriptors=descriptors
        )

        self.clear_cache()
        return self

    def update_static_metadata(
        self, feature_name, feature_type=None, settings=None, **kwargs
    ):
        """
        Update static metadata for a specific feature.
        Systematically triggers cache clearing.

        Args:
            feature_name: Name of the static feature to update.
            feature_type: Optional new feature type (categorical/numerical/textual).
            settings: Optional new settings (dict or dataclass, overridden by kwargs).
            **kwargs: Individual settings fields to update (highest priority).

        Returns:
            self for chaining.

        Raises:
            ValueError: If feature not found in static metadata.
            TypeError: If settings is not dict or dataclass.

        Examples:
            >>> seq.update_static_metadata("country", feature_type="categorical")
            >>> seq.update_static_metadata("country", categories=["FR", "US"], ordered=False)
        """
        if feature_name not in self.metadata.static_descriptors:
            raise ValueError(f"Feature '{feature_name}' not found in static metadata.")

        descriptors = self.metadata.static_descriptors.copy()

        # Use generic helper to update descriptor
        descriptors[feature_name] = self._update_descriptor(
            current_descriptor=descriptors[feature_name],
            type_param_name="feature_type",
            new_type=feature_type,
            settings=settings,
            **kwargs,
        )

        # Update metadata
        self._metadata = dataclasses.replace(
            self.metadata, static_descriptors=descriptors
        )

        self.clear_cache()
        return self
