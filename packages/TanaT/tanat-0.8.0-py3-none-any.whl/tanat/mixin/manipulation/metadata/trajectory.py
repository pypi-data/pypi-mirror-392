#!/usr/bin/env python3
"""
Trajectory metadata mixin.
"""

import dataclasses

from ....metadata.trajectory import TrajectoryMetadata
from ....time.granularity import Granularity
from .base import MetadataMixin


class TrajectoryMetadataMixin(MetadataMixin):
    """
    Metadata mixin for Trajectory and TrajectoryPool.

    Handles metadata inference, validation, and coherence checking
    specific to trajectory-level data.
    """

    def _validate_metadata(self, metadata):
        """
        Validate and normalize input metadata.

        Args:
            metadata: None, dict, or TrajectoryMetadata instance.

        Returns:
            TrajectoryMetadata instance or None.

        Raises:
            ValueError: If metadata format is invalid.
        """
        if metadata is None:
            return None
        if isinstance(metadata, dict):
            return TrajectoryMetadata(**metadata)
        if isinstance(metadata, TrajectoryMetadata):
            return metadata
        raise ValueError("Metadata must be a dict or TrajectoryMetadata instance.")

    def _infer_metadata(self, metadata):
        """
        Infer complete metadata from trajectory data.

        Aggregates metadata from all sequences and validates coherence.

        Args:
            metadata: Optional existing metadata to complete.

        Returns:
            Complete TrajectoryMetadata instance.
        """
        return TrajectoryMetadata.from_trajectory(trajectory=self, metadata=metadata)

    def _set_granularity(self, value):
        """
        Set unified granularity for trajectory metadata.

        This affects all sequences in the trajectory.

        Args:
            value: Granularity value (string or Granularity enum).
        """
        granularity = Granularity.from_str(value)
        self._metadata = dataclasses.replace(self.metadata, granularity=granularity)

    def validate_temporal_coherence(self):
        """
        Validate that all sequences share the same temporal configuration.

        Raises:
            TemporalIncoherenceError: If sequences have incompatible temporal configs.
        """
        sequence_metadatas = {
            name: seqpool.metadata for name, seqpool in self._sequence_pools.items()
        }
        self._metadata.validate_coherence(sequence_metadatas)

    def update_temporal_metadata(
        self, temporal_type=None, granularity=None, settings=None, **kwargs
    ):
        """
        Update temporal metadata for trajectory and propagate to all sequences.
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
            >>> traj.update_temporal_metadata(format="%Y-%m-%d")
            >>> traj.update_temporal_metadata(granularity="HOUR")
            >>> traj.update_temporal_metadata(temporal_type="timestep", min_value=0)
        """
        # Use generic helper to update descriptor
        descriptor_dict = self._update_descriptor(
            current_descriptor=self.metadata.temporal_descriptor,
            type_param_name="temporal_type",
            new_type=temporal_type,
            settings=settings,
            **kwargs,
        )

        # Determine final granularity
        final_granularity = (
            granularity if granularity is not None else self.metadata.granularity
        )

        # Update trajectory metadata
        self._metadata = dataclasses.replace(
            self.metadata,
            temporal_descriptor=descriptor_dict,
            granularity=final_granularity,
        )

        # Propagate to all sequences
        target_type = descriptor_dict["temporal_type"]
        settings_dict = descriptor_dict["settings"]

        for seqpool in self._sequence_pools.values():
            seqpool.update_temporal_metadata(
                temporal_type=target_type,
                granularity=final_granularity,
                settings=settings_dict,
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
            >>> traj.update_static_metadata("country", feature_type="categorical")
            >>> traj.update_static_metadata("country", categories=["FR", "US"])
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
