#!/usr/bin/env python3
"""Trajectory descriptor."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict

import pandas as pd

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin

from .sequence.base import BaseSequenceDescription

LOGGER = logging.getLogger(__name__)


@dataclass
class TrajectoryDescription:
    """
    Description of a trajectory (collection of sequences).

    A trajectory consists of multiple named sequence pools sharing the same id_column.
    This description contains:
    - Aggregate information about the trajectory (n_sequences)
    - Individual descriptions for each sequence pool

    Attributes:
        n_sequences (int): Number of sequence pools in the trajectory (scalar).
        sequence_descriptions (dict): Dictionary mapping sequence names to their descriptions.
            Keys: sequence names (e.g., "hospitalization", "prescriptions")
            Values: BaseSequenceDescription instances
    """

    n_sequences: Optional[int] = None
    sequence_descriptions: Optional[Dict[str, BaseSequenceDescription]] = None

    def to_metadata(self, separator="_"):
        """
        Generate metadata dictionary for all trajectory metrics.

        Args:
            separator: Separator between sequence name and metric name.

        Returns:
            dict: Combined metadata from all sequence descriptions with format:
                {
                    'column_name': {
                        'dtype': 'numerical',
                        'settings': {
                            'dtype': 'Int32' or 'float32',
                            'min_value': float,
                            'max_value': float,
                        }
                    }
                }
        """
        metadata = {}

        # Add metadata for n_sequences (trajectory-level metric)
        metadata["n_sequences"] = {
            "feature_type": "numerical",
            "settings": {
                "dtype": "Int32",
                "min_value": float(self.n_sequences),
                "max_value": float(self.n_sequences),
            },
        }

        # Add metadata from each sequence description
        for seq_name, seq_desc in self.sequence_descriptions.items():
            # Generate metadata for this sequence with proper prefix
            prefix = f"{seq_name}{separator}"
            seq_metadata = seq_desc.to_metadata(prefix=prefix)

            # Merge into trajectory metadata
            metadata.update(seq_metadata)

        return metadata

    def to_dataframe(self, trajectory_id=None, index_name=None, separator="_"):
        """
        Convert trajectory description to DataFrame.

        Concatenates all sequence descriptions horizontally, adding prefixes
        to column names to avoid conflicts.

        Args:
            trajectory_id: Optional trajectory ID to use as index for single trajectory.
                If provided, passed to sequence descriptions for proper indexing.
            index_name (str, optional): Name for the DataFrame index (typically id_column).
            separator (str): Separator between sequence name and metric name.
                Default: "_" (e.g., "events_length", "states_entropy")

        Returns:
            pd.DataFrame: Concatenated descriptions.
                - First column: n_sequences (scalar repeated for all rows)
                - Remaining columns: prefixed metrics from each sequence
                - Index: Named with index_name (one row per entity)
        """
        if not self.sequence_descriptions:
            # No sequences: return empty DataFrame with just n_sequences
            df = pd.DataFrame({"n_sequences": [self.n_sequences]})
            if index_name:
                df.index.name = index_name
            return df

        all_dfs = []

        for seq_name, seq_desc in self.sequence_descriptions.items():
            # Convert sequence description to DataFrame
            # For single trajectory: pass trajectory_id to get proper index
            df = seq_desc.to_dataframe(sequence_id=trajectory_id, index_name=index_name)

            # Add prefix to column names
            df = df.add_prefix(f"{seq_name}{separator}")

            all_dfs.append(df)

        # Concatenate horizontally (along columns, same index)
        result = pd.concat(all_dfs, axis=1)

        # Add n_sequences as first column (scalar repeated for all rows)
        result.insert(0, "n_sequences", self.n_sequences)

        return result


class TrajectoryDescriptor(Cachable, SettingsMixin):
    """
    Descriptor for computing trajectory-level statistics.

    A trajectory descriptor computes descriptions for all sequence pools
    in the trajectory and aggregates them into a single description.
    """

    def __init__(self, trajectory, settings=None):
        """
        Initialize trajectory descriptor.

        Args:
            trajectory: The Trajectory or TrajectoryPool instance to describe.
            settings: Optional settings (inherits from trajectory if not provided).
        """
        SettingsMixin.__init__(self, settings or trajectory.settings)
        Cachable.__init__(self)
        self._trajectory = trajectory

    @Cachable.caching_method()
    def describe(self, dropna=False):
        """
        Compute trajectory description.

        Args:
            dropna (bool): If True, silently drops NaT values in temporal columns.
                If False, raises ValueError when NaT values are encountered.
                Default: False.

        Returns:
            TrajectoryDescription: Description containing:
                - n_sequences: Number of sequence pools (scalar)
                - sequence_descriptions: Dict of {seq_name: BaseSequenceDescription}

        Raises:
            ValueError: If dropna=False and any sequence contains NaT values.
        """
        return self._compute_description(dropna=dropna)

    def _compute_description(self, dropna=False):
        """
        Internal method to compute trajectory description.

        Strategy:
        - For TrajectoryPool: iterate over _sequence_pools (dict of SequencePool)
        - For Trajectory (single): iterate over sequences property (dict of Sequence)

        Args:
            dropna (bool): Whether to drop NaT values in temporal columns.

        Returns:
            TrajectoryDescription: Computed description.
        """
        # Determine which property to iterate on
        # - TrajectoryPool: sequence_pools (SequencePool instances)
        # - Trajectory: sequences (Sequence instances for this trajectory_id)
        if hasattr(self._trajectory, "sequences"):
            # Single trajectory: use sequences property (dict of Sequence)
            sequence_objects = self._trajectory.sequences
        else:
            # Pool: use sequence_pools (dict of SequencePool)
            sequence_objects = self._trajectory.sequence_pools

        # Count number of sequences
        n_sequences = len(sequence_objects)

        # Compute description for each sequence
        sequence_descriptions = {}

        for seq_name, seq_obj in sequence_objects.items():
            # Get descriptor and compute description
            seq_descriptor = seq_obj._descriptor  # pylint: disable=protected-access
            seq_desc = seq_descriptor.describe(dropna=dropna)
            sequence_descriptions[seq_name] = seq_desc

        return TrajectoryDescription(
            n_sequences=n_sequences,
            sequence_descriptions=sequence_descriptions,
        )
