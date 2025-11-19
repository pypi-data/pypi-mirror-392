#!/usr/bin/env python3
"""
Sequence metadata.
"""

import logging

from pydantic import Field
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.fallback.typing import Dict

from .base.temporal import TemporalMetadata
from .base.static import StaticMetadata
from .descriptor.feature.config import FeatureDescriptor


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class SequenceMetadata(TemporalMetadata, StaticMetadata):
    """
    Metadata for sequence container.

    Attributes:
        temporal_descriptor: Temporal descriptor configuration.
        granularity: Time granularity for temporal data.
        static_descriptors: Dict of static feature descriptors.
        entity_descriptors: Dict of entity (time-varying) feature descriptors.

    Note:
        - temporal_descriptor and granularity are inherited from TemporalMetadata.
        - static_descriptors are inherited from StaticMetadata.
    """

    entity_descriptors: Dict[str, FeatureDescriptor] = Field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize coercer caches from both parent classes.
        """
        # Call parent __post_init__ methods explicitly
        TemporalMetadata.__post_init__(self)
        StaticMetadata.__post_init__(self)
        # Initialize entity coercer cache
        self._entity_coercers = {}

    def validate_completeness(self, settings):
        """
        Check if metadata is complete for a Sequence.

        Args:
            settings: SequenceSettings instance.

        Returns:
            bool: True if all components are complete.
        """
        if not TemporalMetadata.is_complete(self):
            return False

        if not self._are_entity_features_complete(settings):
            return False

        if not self._are_static_features_complete(settings):
            return False

        return True

    def _are_entity_features_complete(self, settings):
        """
        Check if all entity features are complete.

        Args:
            settings: SequenceSettings instance.

        Returns:
            bool: True if all entity features are complete.
        """
        entity_features = settings.entity_features or []

        for feat_name in entity_features:
            if not self._is_entity_feature_complete(feat_name):
                return False

        return True

    def _is_entity_feature_complete(self, feat_name):
        """
        Check if a single entity feature is complete.

        Args:
            feat_name: Feature name to check.

        Returns:
            bool: True if the feature is complete.
        """
        if feat_name not in self.entity_descriptors:
            LOGGER.debug("Entity feature '%s' missing from metadata", feat_name)
            return False

        descriptor = self.entity_descriptors[feat_name]

        if descriptor.settings is None:
            LOGGER.debug("Entity feature '%s' has no settings", feat_name)
            return False

        if descriptor.settings.has_missing_required_fields():
            LOGGER.debug("Entity feature '%s' has incomplete settings", feat_name)
            return False

        return True

    def _are_static_features_complete(self, settings):
        """
        Check if all static features are complete.

        Args:
            settings: SequenceSettings instance.

        Returns:
            bool: True if all static features are complete.
        """
        static_features = settings.static_features or []
        return StaticMetadata.is_complete(self, feature_names=static_features)

    @classmethod
    def from_sequence(cls, sequence, metadata=None):
        """
        Infer/complete metadata from a Sequence.

        Applies 3-rule inference logic to each component independently.

        Args:
            sequence: Sequence or SequencePool instance.
            metadata: Optional existing metadata to complete.

        Returns:
            SequenceMetadata: Complete SequenceMetadata instance.
        """
        # pylint: disable=protected-access
        # Check if already complete
        if metadata and metadata.validate_completeness(sequence.settings):
            LOGGER.debug("Sequence metadata already complete, skipping inference")
            return metadata

        # Do not use `.sequence_data` property to avoid recursion
        sequence_data = sequence._get_raw_sequence_data()
        # infer if missing
        temporal_inferred = cls._infer_temporal_metadata(
            sequence, sequence_data, metadata
        )
        entity_descriptors = cls._infer_entity_descriptors(
            sequence, sequence_data, metadata
        )

        static_inferred = {}
        if sequence._static_data is None:
            return cls(
                temporal_descriptor=temporal_inferred.temporal_descriptor,
                granularity=temporal_inferred.granularity,
                static_descriptors={},
                entity_descriptors=entity_descriptors,
            )

        static_data = sequence._get_raw_static_data()
        static_inferred = cls._infer_static_metadata(sequence, static_data, metadata)
        return cls(
            temporal_descriptor=temporal_inferred.temporal_descriptor,
            granularity=temporal_inferred.granularity,
            static_descriptors=static_inferred.static_descriptors,
            entity_descriptors=entity_descriptors,
        )

    @classmethod
    def _infer_temporal_metadata(cls, sequence, df, metadata):
        """
        Infer temporal metadata component.

        Args:
            sequence: Sequence instance.
            df: Raw sequence DataFrame.
            metadata: Optional existing metadata.

        Returns:
            TemporalMetadata: Inferred temporal metadata.
        """
        temporal_cols = sequence.settings.temporal_columns(standardize=False)
        return TemporalMetadata.infer_from_dataframe(
            df, temporal_cols, existing=metadata
        )

    @classmethod
    def _infer_entity_descriptors(cls, sequence, df, metadata):
        """
        Infer entity feature descriptors.

        Args:
            sequence: Sequence instance.
            df: Raw sequence DataFrame.
            metadata: Optional existing metadata.

        Returns:
            dict: Dictionary of entity descriptors.
        """
        entity_cols = sequence.settings.entity_features or []
        entity_descriptors = {}
        existing_entity = metadata.entity_descriptors if metadata else {}

        for col in entity_cols:
            entity_descriptors[col] = cls._infer_single_entity_descriptor(
                col, df, existing_entity
            )

        return entity_descriptors

    @classmethod
    def _infer_single_entity_descriptor(cls, col, df, existing_entity):
        """
        Infer or complete a single entity descriptor.

        Args:
            col: Column name.
            df: DataFrame.
            existing_entity: Existing entity descriptors dict.

        Returns:
            FeatureDescriptor: Inferred or completed descriptor.
        """
        if col not in existing_entity:
            # Rule 1: Missing descriptor → full inference
            LOGGER.debug("Inferred entity feature '%s' from data", col)
            return FeatureDescriptor.infer(df[col])

        descriptor = existing_entity[col]

        if descriptor.settings is None:
            # Rule 2: Type hint only → infer with hint
            LOGGER.debug("Completed entity feature '%s' with type hint", col)
            return FeatureDescriptor.infer(df[col], type_hint=descriptor.feature_type)

        if descriptor.settings.has_missing_required_fields():
            # Rule 3: Incomplete settings → complete
            completed = descriptor.settings.complete_from_data(df[col])
            LOGGER.debug("Completed entity feature '%s' settings from data", col)
            return FeatureDescriptor(
                feature_type=descriptor.feature_type, settings=completed
            )

        # Already complete
        return descriptor

    @classmethod
    def _infer_static_metadata(cls, sequence, df, metadata):
        """
        Infer static metadata component.

        Args:
            sequence: Sequence instance.
            df: Raw sequence DataFrame.
            metadata: Optional existing metadata.

        Returns:
            StaticMetadata: Inferred static metadata.
        """
        static_cols = sequence.settings.static_features or []
        return StaticMetadata.infer_from_dataframe(df, static_cols, existing=metadata)

    def prepare_sequence_data(self, df, settings):
        """
        Prepare sequence DataFrame applying coercion to temporal, and entity features.

        Args:
            df: Input DataFrame.
            settings: SequenceSettings.

        Returns:
            pd.DataFrame: DataFrame with coerced columns.
        """
        data = df.copy()
        data = self._coerce_temporal_columns(data, settings)
        data = self._coerce_entity_columns(data)
        return data

    def _coerce_temporal_columns(self, data, settings):
        """
        Coerce temporal columns in the DataFrame.

        Args:
            data: DataFrame to modify.
            settings: SequenceSettings.

        Returns:
            pd.DataFrame: DataFrame with coerced temporal columns.
        """
        temporal_cols = settings.temporal_columns(standardize=False)
        for col in temporal_cols:
            if col in data.columns:
                data[col] = TemporalMetadata.coerce(self, data[col])
        return data

    def _coerce_entity_columns(self, data):
        """
        Coerce entity feature columns in the DataFrame.

        Args:
            data: DataFrame to modify.

        Returns:
            pd.DataFrame: DataFrame with coerced entity columns.
        """
        for col in self.entity_descriptors:
            if col in data.columns:
                data[col] = self._coerce_entity_column(col, data[col])
        return data

    def _coerce_entity_column(self, col, series):
        """
        Coerce a single entity column.

        Args:
            col: Column name.
            series: Pandas Series to coerce.

        Returns:
            pd.Series: Coerced series.
        """
        if col not in self._entity_coercers:
            descriptor = self.entity_descriptors[col]
            self._entity_coercers[col] = descriptor.get_descriptor()
        return self._entity_coercers[col].coerce(series)

    def describe(self, verbose=False):
        """
        Human-readable description of complete metadata.

        Shows temporal, entity, and static components.

        Args:
            verbose: If True, include descriptor details.

        Returns:
            str: Formatted string.
        """
        lines = []

        # Temporal
        lines.append(TemporalMetadata.describe(self, verbose))
        lines.append("")

        # Entity features
        lines.extend(self._describe_entity_features(verbose))
        lines.append("")

        # Static features
        lines.append(StaticMetadata.describe(self, verbose))

        return "\n".join(lines)

    def _describe_entity_features(self, verbose):
        """
        Generate description lines for entity features.

        Args:
            verbose: If True, include detailed descriptor information.

        Returns:
            list: Lines describing entity features.
        """
        lines = [f"Entity Features ({len(self.entity_descriptors)}):"]

        if not self.entity_descriptors:
            lines.append("  (none)")
        else:
            for name, desc in self.entity_descriptors.items():
                lines.append(self._format_entity_feature(name, desc, verbose))

        return lines

    @staticmethod
    def _format_entity_feature(name, desc, verbose):
        """
        Format a single entity feature description.

        Args:
            name: Feature name.
            desc: Feature descriptor.
            verbose: If True, include settings details.

        Returns:
            str: Formatted feature description.
        """
        if verbose and desc.settings:
            return f"  - {name}: {desc.feature_type} | {desc.settings}"
        return f"  - {name}: {desc.feature_type}"
