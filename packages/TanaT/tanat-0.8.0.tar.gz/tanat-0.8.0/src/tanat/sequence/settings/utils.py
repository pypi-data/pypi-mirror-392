#!/usr/bin/env python3
"""
Utility functions for sequence settings.
"""


def _create_child_settings(base_settings, **overrides):
    """
    Create child settings with specified overrides.

    Args:
        base_settings: Base settings instance to copy from.
        **overrides: Attributes to override in new settings.

    Returns:
        New settings instance with overrides applied.
    """
    settings_dict = {}
    for field_name in base_settings.__dataclass_fields__:
        settings_dict[field_name] = getattr(base_settings, field_name)
    settings_dict.update(overrides)
    return base_settings.__class__(**settings_dict)


def _validate_no_column_conflicts(settings):
    """
    Validate that column names are not duplicated across settings.

    Rules:
        - ID column must be unique across all settings
        - Temporal columns (if present) cannot overlap with entity features
        - Static features and entity features MAY share column names
        - Temporal columns MAY overlap with static features

    Args:
        settings: A settings dataclass instance with attributes:
            - id_column (required)
            - entity_features (optional)
            - static_features (optional)
            - temporal_columns (optional, can be method or attribute)

    Raises:
        ValueError: If duplicate column names are found between
            incompatible settings.
    """
    # ID column (required)
    id_col = {settings.id_column}
    #   Entity features (optional)
    entity_features = getattr(settings, "entity_features", None)
    entity_cols = set(entity_features) if entity_features else set()
    # Static features (optional)
    static_features = getattr(settings, "static_features", None)
    static_cols = set(static_features) if static_features else set()
    # Temporal columns (optional, can be method or attribute)
    temporal_columns = getattr(settings, "temporal_columns", None)
    if callable(temporal_columns):
        temporal_columns = temporal_columns()
    temporal_cols = set(temporal_columns) if temporal_columns else set()

    # Collect all conflicts
    conflicts = []
    # Conflicts with temporal columns (if present)
    if temporal_cols:
        temporal_entity_overlap = temporal_cols & entity_cols
        if temporal_entity_overlap:
            conflicts.append(
                f"  - Temporal columns vs Entity features: {sorted(temporal_entity_overlap)}"
            )

        id_temporal_overlap = id_col & temporal_cols
        if id_temporal_overlap:
            conflicts.append(
                f"  - ID column vs Temporal columns: {sorted(id_temporal_overlap)}"
            )

    # Conflicts with entity features (if present)
    if entity_cols:
        id_entity_overlap = id_col & entity_cols
        if id_entity_overlap:
            conflicts.append(
                f"  - ID column vs Entity features: {sorted(id_entity_overlap)}"
            )

    # Static conflicts
    if static_cols:
        id_static_overlap = id_col & static_cols
        if id_static_overlap:
            conflicts.append(
                f"  - ID column vs Static features: {sorted(id_static_overlap)}"
            )
    # Raise error if any conflicts found
    if conflicts:
        conflict_msg = "\n".join(conflicts)
        raise ValueError(
            f"Column name conflicts detected:\n{conflict_msg}\n"
            f"Note: Static features may overlap with Entity features and Temporal columns."
        )
