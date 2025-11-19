#!/usr/bin/env python3
"""
Trajectory metadata.
"""

import logging
from collections import defaultdict

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from .base.temporal import TemporalMetadata
from .base.static import StaticMetadata
from .exception import TemporalIncoherenceError

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class TrajectoryMetadata(TemporalMetadata, StaticMetadata):
    """
    Metadata for trajectory container.

    Attributes:
        temporal_descriptor: Unified temporal descriptor (common to all sequences).
        granularity: Unified time granularity (common to all sequences).
        static_descriptors: Dict of static feature descriptors.

    Note:
        - temporal_descriptor and granularity are inherited from TemporalMetadata.
        - static_descriptors are inherited from StaticMetadata.
    """

    def __post_init__(self):
        """Initialize coercer caches from both parent classes."""
        TemporalMetadata.__post_init__(self)
        StaticMetadata.__post_init__(self)

    def validate_completeness(self, settings):
        """
        Check if metadata is complete for a Trajectory.

        Delegates to inherited component methods.

        Args:
            settings: TrajectorySettings instance.

        Returns:
            True if all components are complete.
        """
        temporal_complete = TemporalMetadata.is_complete(self)
        static_complete = StaticMetadata.is_complete(
            self, feature_names=settings.static_features
        )
        return temporal_complete and static_complete

    def validate_coherence(self, sequence_metadatas):
        """
        Validate that all sequences match the trajectory's temporal configuration.

        The trajectory metadata is the source of truth. This method ensures that
        all sequences conform to the temporal_type, granularity, and settings
        declared in the trajectory metadata.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Raises:
            TemporalIncoherenceError: If sequences don't match trajectory configuration.
        """
        if not sequence_metadatas:
            return

        if self.temporal_descriptor is None:
            return

        self._validate_sequences_against_trajectory(sequence_metadatas)

    def _validate_sequences_against_trajectory(self, sequence_metadatas):
        """
        Check that all sequences conform to trajectory's temporal configuration.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Raises:
            TemporalIncoherenceError: If mismatches are found.
        """
        mismatches = self._collect_temporal_mismatches(sequence_metadatas)
        self._report_temporal_mismatches(mismatches)

    def _collect_temporal_mismatches(self, sequence_metadatas):
        """
        Collect sequences that don't match trajectory's temporal configuration.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Returns:
            Dict with keys 'temporal_type', 'granularity', 'settings' containing
            lists of mismatched sequences.
        """
        ref_temporal_type = self.temporal_descriptor.temporal_type
        # ref_granularity = self.granularity
        ref_settings = self.temporal_descriptor.settings

        mismatches = {"temporal_type": [], "granularity": [], "settings": []}

        for seq_name, seq_meta in sequence_metadatas.items():
            seq_temporal = seq_meta.temporal_descriptor
            seq_temporal_type = seq_temporal.temporal_type
            # seq_granularity = seq_meta.granularity
            seq_settings = seq_temporal.settings

            if seq_temporal_type != ref_temporal_type:
                mismatches["temporal_type"].append((seq_name, seq_temporal_type))

            # TODO: Granularity validation is currently disabled.
            # Consider enabling this check if strict granularity matching becomes required.
            # if seq_granularity != ref_granularity:
            #     mismatches["granularity"].append((seq_name, seq_granularity))

            if ref_settings is not None:
                if not ref_settings.is_compatible_with(seq_settings):
                    mismatches["settings"].append(seq_name)

        return mismatches

    def _report_temporal_mismatches(self, mismatches):
        """
        Raise errors for any temporal mismatches found.

        Args:
            mismatches: Dict containing lists of mismatched sequences.

        Raises:
            TemporalIncoherenceError: If any mismatches exist.
        """
        ref_temporal_type = self.temporal_descriptor.temporal_type
        ref_granularity = self.granularity

        if mismatches["temporal_type"]:
            details = "\n".join(
                f"  - {seq_name}: {seq_type}"
                for seq_name, seq_type in mismatches["temporal_type"]
            )
            raise TemporalIncoherenceError(
                f"The following sequences don't match trajectory temporal_type "
                f"({ref_temporal_type}):\n{details}\n\n"
                f"All sequences must use the same temporal_type as the trajectory."
            )

        if mismatches["granularity"]:
            details = "\n".join(
                f"  - {seq_name}: {seq_gran}"
                for seq_name, seq_gran in mismatches["granularity"]
            )
            raise TemporalIncoherenceError(
                f"The following sequences don't match trajectory granularity "
                f"({ref_granularity}):\n{details}\n\n"
                f"All sequences must use the same granularity as the trajectory."
            )

        if mismatches["settings"]:
            details = "\n".join(f"  - {seq}" for seq in mismatches["settings"])
            raise TemporalIncoherenceError(
                f"The following sequences have incompatible temporal settings:\n"
                f"{details}\n\n"
                f"All sequences must have compatible settings with the trajectory."
            )

    @classmethod
    def aggregate_from_sequences(cls, sequence_metadatas):
        """
        Aggregate trajectory metadata from sequence metadatas.

        Extracts common temporal metadata and validates coherence.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Returns:
            TrajectoryMetadata instance.

        Raises:
            TemporalIncoherenceError: If sequences have incompatible temporal configs.
        """
        # Handle empty trajectory (no sequences yet)
        if not sequence_metadatas:
            return cls()

        first_meta = next(iter(sequence_metadatas.values()))
        ref_temporal_desc = first_meta.temporal_descriptor
        ref_granularity = first_meta.granularity

        cls._validate_sequence_uniformity(sequence_metadatas)

        return cls(
            temporal_descriptor=ref_temporal_desc,
            granularity=ref_granularity,
        )

    @classmethod
    def _validate_sequence_uniformity(cls, sequence_metadatas):
        """
        Validate that all sequences have the same temporal type and granularity.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Raises:
            TemporalIncoherenceError: If sequences differ in temporal type or granularity.
        """
        grouped_data = cls._group_sequences_by_temporal_properties(sequence_metadatas)
        cls._report_sequence_uniformity_errors(grouped_data)

    @classmethod
    def _group_sequences_by_temporal_properties(cls, sequence_metadatas):
        """
        Group sequences by their temporal type and granularity.

        Args:
            sequence_metadatas: Dict mapping sequence names to their SequenceMetadata.

        Returns:
            Dict with 'temporal_types' and 'granularities' keys, each containing
            a dict mapping property values to lists of sequence names.
        """
        temporal_types = defaultdict(list)
        granularities = defaultdict(list)

        for seq_name, seq_meta in sequence_metadatas.items():
            seq_temporal_desc = seq_meta.temporal_descriptor
            seq_granularity = seq_meta.granularity

            temporal_types[seq_temporal_desc.temporal_type].append(seq_name)
            granularities[seq_granularity].append(seq_name)

        return {"temporal_types": temporal_types, "granularities": granularities}

    @classmethod
    def _report_sequence_uniformity_errors(cls, grouped_data):
        """
        Raise errors if sequences have multiple temporal types or granularities.

        Args:
            grouped_data: Dict with 'temporal_types' and 'granularities' groupings.

        Raises:
            TemporalIncoherenceError: If non-uniform temporal properties are found.
        """
        temporal_types = grouped_data["temporal_types"]
        granularities = grouped_data["granularities"]

        if len(temporal_types) > 1:
            details = "\n".join(
                f"  - {ttype}: {', '.join(seqs)}"
                for ttype, seqs in sorted(temporal_types.items())
            )
            raise TemporalIncoherenceError(
                f"Temporal type mismatch across sequences:\n{details}\n\n"
                f"All sequences must use the same temporal_type."
            )

        if len(granularities) > 1:
            details = "\n".join(
                f"  - {gran}: {', '.join(seqs)}" for gran, seqs in granularities.items()
            )
            raise TemporalIncoherenceError(
                f"Granularity mismatch across sequences:\n{details}\n\n"
                f"All sequences must use the same granularity."
            )

    @classmethod
    def from_trajectory(cls, trajectory, metadata=None):
        """
        Infer/complete metadata from Trajectory.

        Logic:
        1. Aggregate temporal config from sequences (validates inter-sequence coherence)
        2. If user provided metadata:
           - Use user's temporal config if provided (priority over sequences)
           - Validate that sequences conform to user's config
           - Complete missing fields from aggregation
        3. Infer static descriptors from trajectory data if needed

        Args:
            trajectory: Trajectory or TrajectoryPool instance.
            metadata: Optional user-provided metadata (can be partial).

        Returns:
            Complete TrajectoryMetadata instance.

        Raises:
            TemporalIncoherenceError: If user-provided config is incompatible with sequences.
        """
        # pylint: disable=protected-access
        seq_metadatas = {
            name: seqpool.metadata
            for name, seqpool in trajectory._sequence_pools.items()
        }

        aggregated_meta = cls.aggregate_from_sequences(seq_metadatas)
        final_meta = cls._merge_with_user_metadata(
            aggregated_meta, metadata, seq_metadatas
        )

        return cls._complete_static(final_meta, trajectory, metadata)

    @classmethod
    def _merge_with_user_metadata(cls, aggregated_meta, user_metadata, seq_metadatas):
        """
        Merge aggregated metadata with user-provided metadata.

        Args:
            aggregated_meta: TrajectoryMetadata aggregated from sequences.
            user_metadata: Optional user-provided metadata.
            seq_metadatas: Dict of sequence metadatas for validation.

        Returns:
            TrajectoryMetadata with merged configuration.

        Raises:
            TemporalIncoherenceError: If user config is incompatible with sequences.
        """
        if user_metadata is None:
            LOGGER.debug("No user metadata provided, using aggregated from sequences")
            return aggregated_meta

        LOGGER.debug("Merging user-provided metadata with aggregated")

        final_temporal = (
            user_metadata.temporal_descriptor or aggregated_meta.temporal_descriptor
        )
        final_granularity = user_metadata.granularity or aggregated_meta.granularity

        final_meta = cls(
            temporal_descriptor=final_temporal,
            granularity=final_granularity,
            static_descriptors=(
                dict(user_metadata.static_descriptors)
                if user_metadata.static_descriptors
                else {}
            ),
        )

        LOGGER.debug("Validating sequences against user-provided configuration")
        final_meta.validate_coherence(seq_metadatas)

        return final_meta

    @classmethod
    def _complete_static(cls, trajectory_meta, trajectory, user_metadata=None):
        """
        Complete static descriptors from trajectory data.

        Args:
            trajectory_meta: TrajectoryMetadata to complete.
            trajectory: Trajectory instance with data.
            user_metadata: Optional user-provided metadata to preserve.

        Returns:
            TrajectoryMetadata with completed static descriptors.
        """
        # pylint: disable=protected-access
        static_cols = trajectory.settings.static_features

        if trajectory._static_data is not None and static_cols:
            LOGGER.debug("Inferring static descriptors from trajectory data")
            existing_meta = user_metadata if user_metadata else trajectory_meta
            static_inferred = StaticMetadata.infer_from_dataframe(
                trajectory._get_raw_static_data(),
                static_cols,
                existing=existing_meta,
            )
            trajectory_meta.static_descriptors = static_inferred.static_descriptors

        return trajectory_meta

    def describe(self, verbose=False):
        """
        Human-readable description of trajectory metadata.

        Delegates to inherited component methods.

        Args:
            verbose: If True, include descriptor details.

        Returns:
            Formatted string.
        """
        temporal_desc = TemporalMetadata.describe(self, verbose)
        static_desc = StaticMetadata.describe(self, verbose)

        return f"{temporal_desc}\n\n{static_desc}"
