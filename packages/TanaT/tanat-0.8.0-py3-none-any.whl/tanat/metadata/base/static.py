#!/usr/bin/env python3
"""
Static features metadata component.
"""

import logging

from pydantic.dataclasses import dataclass, Field
from pypassist.fallback.typing import Dict

from ..descriptor.feature.config import FeatureDescriptor

LOGGER = logging.getLogger(__name__)


@dataclass
class StaticMetadata:
    """
    Metadata for static (time-invariant) features.
    """

    static_descriptors: Dict[str, FeatureDescriptor] = Field(default_factory=dict)

    def __post_init__(self):
        """Initialize coercer cache."""
        self._coercers = {}

    def is_complete(self, feature_names=None):
        """
        Check if all static features have complete descriptors.

        Args:
            feature_names: Optional list of expected feature names.
                If None, checks all present descriptors.

        Returns:
            bool: True if all features have complete descriptors, False otherwise.
        """
        features_to_check = self._get_features_to_check(feature_names)

        if not features_to_check:
            return True

        for feat_name in features_to_check:
            if not self._is_feature_complete(feat_name):
                return False

        return True

    def _get_features_to_check(self, feature_names):
        """
        Determine which features to check for completeness.

        Args:
            feature_names: Optional list of feature names.

        Returns:
            list: List of feature names to check.
        """
        if feature_names is None:
            return list(self.static_descriptors.keys())
        return feature_names

    def _is_feature_complete(self, feat_name):
        """
        Check if a single static feature is complete.

        Args:
            feat_name: Feature name to check.

        Returns:
            bool: True if the feature is complete.
        """
        if feat_name not in self.static_descriptors:
            LOGGER.debug("Static feature '%s' missing from metadata", feat_name)
            return False

        descriptor = self.static_descriptors[feat_name]

        if descriptor.settings is None:
            LOGGER.debug("Static feature '%s' has no settings", feat_name)
            return False

        if descriptor.settings.has_missing_required_fields():
            LOGGER.debug("Static feature '%s' has incomplete settings", feat_name)
            return False

        return True

    def prepare_static_data(self, df, settings):
        """
        Prepare static DataFrame applying coercion to static features.

        Args:
            df: Input DataFrame.
            settings: SequenceSettings or TrajectorySettings.

        Returns:
            pd.DataFrame: DataFrame with coerced static columns.
        """
        data = df.copy()
        data = self._coerce_static_columns(data, settings)
        return data

    def _coerce_static_columns(self, data, settings):
        """
        Coerce static feature columns in the DataFrame.

        Args:
            data: DataFrame to modify.
            settings: SequenceSettings.

        Returns:
            pd.DataFrame: DataFrame with coerced static columns.
        """
        static_features = settings.static_features or []
        for col in static_features:
            if col in data.columns:
                data[col] = StaticMetadata.coerce(self, data[col], col)
        return data

    def coerce(self, series, column_name):
        """
        Coerce a static feature column using cached coercer.

        Args:
            series: Pandas Series to coerce.
            column_name: Name of the feature.

        Returns:
            pd.Series: Coerced Series with proper feature type.
        """
        if column_name not in self._coercers:
            descriptor = self.static_descriptors[column_name]
            self._coercers[column_name] = descriptor.get_descriptor()

        return self._coercers[column_name].coerce(series)

    @classmethod
    def infer_from_dataframe(cls, df, feature_columns, existing=None):
        """
        Infer static metadata from DataFrame using 3-rule logic.

        Rules:
        1. Missing descriptor → full inference
        2. Descriptor without settings → infer with type hint
        3. Incomplete settings → complete from data

        Args:
            df: DataFrame containing static features.
            feature_columns: List of feature column names.
            existing: Optional existing StaticMetadata to complete.

        Returns:
            StaticMetadata: Instance with inferred/completed descriptors.
        """
        existing_descs = existing.static_descriptors if existing else {}
        descriptors = {}

        for col in feature_columns:
            descriptors[col] = cls._infer_single_descriptor(col, df, existing_descs)

        return cls(static_descriptors=descriptors)

    @classmethod
    def _infer_single_descriptor(cls, col, df, existing_descs):
        """
        Infer or complete a single static feature descriptor.

        Args:
            col: Column name.
            df: DataFrame containing the column.
            existing_descs: Dictionary of existing descriptors.

        Returns:
            FeatureDescriptor: Inferred or completed descriptor.
        """
        if col not in existing_descs:
            # Rule 1: Missing descriptor → full inference
            return cls._infer_new_descriptor(col, df)

        # Rule 2 & 3: Complete existing descriptor
        return cls._complete_existing_descriptor(col, df, existing_descs[col])

    @classmethod
    def _infer_new_descriptor(cls, col, df):
        """
        Infer a new descriptor from data (Rule 1).

        Args:
            col: Column name.
            df: DataFrame containing the column.

        Returns:
            FeatureDescriptor: Newly inferred descriptor.
        """
        descriptor = FeatureDescriptor.infer(df[col])
        LOGGER.debug("Inferred static feature '%s' from data", col)
        return descriptor

    @classmethod
    def _complete_existing_descriptor(cls, col, df, descriptor):
        """
        Complete an existing descriptor (Rules 2 & 3).

        Args:
            col: Column name.
            df: DataFrame containing the column.
            descriptor: Existing descriptor to complete.

        Returns:
            FeatureDescriptor: Completed descriptor.
        """
        if descriptor.settings is None:
            # Rule 2: Type hint only → infer with hint
            return cls._complete_with_type_hint(col, df, descriptor)

        if descriptor.settings.has_missing_required_fields():
            # Rule 3: Incomplete settings → complete
            return cls._complete_settings(col, df, descriptor)

        # Already complete
        return descriptor

    @classmethod
    def _complete_with_type_hint(cls, col, df, descriptor):
        """
        Complete descriptor using type hint (Rule 2).

        Args:
            col: Column name.
            df: DataFrame containing the column.
            descriptor: Existing descriptor with type hint.

        Returns:
            FeatureDescriptor: Completed descriptor.
        """
        completed = FeatureDescriptor.infer(df[col], type_hint=descriptor.feature_type)
        LOGGER.debug("Completed static feature '%s' with type hint", col)
        return completed

    @classmethod
    def _complete_settings(cls, col, df, descriptor):
        """
        Complete descriptor settings from data (Rule 3).

        Args:
            col: Column name.
            df: DataFrame containing the column.
            descriptor: Existing descriptor with incomplete settings.

        Returns:
            FeatureDescriptor: Descriptor with completed settings.
        """
        completed_settings = descriptor.settings.complete_from_data(df[col])
        completed_descriptor = FeatureDescriptor(
            feature_type=descriptor.feature_type, settings=completed_settings
        )
        LOGGER.debug("Completed static feature '%s' settings from data", col)
        return completed_descriptor

    def describe(self, verbose=False):
        """
        Human-readable description of static features.

        Args:
            verbose: If True, include descriptor details.

        Returns:
            str: Formatted string describing the static features.
        """
        lines = [f"Static Features ({len(self.static_descriptors)}):"]

        if not self.static_descriptors:
            lines.append("  (none)")
        else:
            lines.extend(self._describe_features(verbose))

        return "\n".join(lines)

    def _describe_features(self, verbose):
        """
        Generate description lines for all features.

        Args:
            verbose: If True, include detailed descriptor information.

        Returns:
            list: Lines describing each feature.
        """
        lines = []
        for name, desc in self.static_descriptors.items():
            lines.append(self._format_feature(name, desc, verbose))
        return lines

    @staticmethod
    def merge_descriptors(descriptors1, descriptors2):
        """
        Merge two descriptor dictionaries.

        Descriptors from descriptors2 override those in descriptors1.

        Args:
            descriptors1: First dict of {feature_name: FeatureDescriptor}.
            descriptors2: Second dict of {feature_name: FeatureDescriptor}.

        Returns:
            dict: Merged descriptors.

        Example:
            >>> desc1 = {'gender': FeatureDescriptor(...)}
            >>> desc2 = {'age': FeatureDescriptor(...), 'score': FeatureDescriptor(...)}
            >>> merged = StaticMetadata.merge_descriptors(desc1, desc2)
            >>> # Result: {'gender': ..., 'age': ..., 'score': ...}
        """
        return {**descriptors1, **descriptors2}

    @staticmethod
    def _format_feature(name, desc, verbose):
        """
        Format a single feature description.

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
