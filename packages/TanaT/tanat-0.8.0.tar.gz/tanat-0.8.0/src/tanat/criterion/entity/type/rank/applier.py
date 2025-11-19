#!/usr/bin/env python3
"""
Rank criterion applier.
"""

import logging

import numpy as np
import pandas as pd

from ...base.applier import EntityCriterionApplier
from .settings import RankCriterion


LOGGER = logging.getLogger(__name__)


class RankEntityCriterionApplier(EntityCriterionApplier, register_name="rank"):
    """
    Applier for rank-based entity filtering.
    """

    SETTINGS_DATACLASS = RankCriterion

    def _resolve_negative_index(self, index, length):
        """
        Resolve negative index to positive using Python semantics.

        Args:
            index: Index to resolve (can be negative)
            length: Length of the sequence

        Returns:
            int: Resolved positive index, clamped to [0, length]

        Examples:
            >>> self._resolve_negative_index(5, 10)   # 5
            >>> self._resolve_negative_index(-2, 10)  # 8
            >>> self._resolve_negative_index(-20, 10) # 0 (clamped)
            >>> self._resolve_negative_index(20, 10)  # 10 (clamped)
        """
        if index < 0:
            resolved = length + index
        else:
            resolved = index

        # Clamp to valid range [0, length]
        return max(0, min(resolved, length))

    def _needs_relative_ranks(self):
        """
        Check if relative ranks computation is needed.

        Optimization: first/last have the same behavior in absolute and relative
        mode (they just take n first/last entities), so we can skip the expensive
        to_relative_rank() computation for these parameters.

        Returns:
            bool: True if relative ranks need to be computed
        """
        # first and last don't need relative ranks (same behavior in both modes)
        if self.settings.first is not None or self.settings.last is not None:
            return False

        # start, end, and ranks actually need relative rank computation
        return self.settings.relative

    def _get_relative_ranks(self, sequence_or_pool):
        """
        Extract relative ranks from sequence or pool.

        Centralized method to avoid code duplication.

        Args:
            sequence_or_pool: Sequence or SequencePool object

        Returns:
            pd.Series: Relative rank values
        """
        rank_data = sequence_or_pool.to_relative_rank()
        rank_column = sequence_or_pool.transformer_settings.relative_rank_column
        return rank_data[rank_column]

    def _compute_ranks_to_keep(self, n_entities, sequence_id=None, relative_ranks=None):
        """
        Compute which ranks to keep based on criterion parameters.

        Args:
            n_entities: Total number of entities in the sequence
            sequence_id: Optional sequence ID for logging
            relative_ranks: Optional Series of relative ranks (for relative mode)

        Returns:
            List of ranks (indices) to keep
        """
        # Handle first/last (works in both absolute and relative mode)
        if self.settings.first is not None:
            if self.settings.first > 0:
                # Positive: first N elements
                return list(range(min(self.settings.first, n_entities)))
            else:
                # Negative: all except last |N| elements
                end = max(
                    0, n_entities + self.settings.first
                )  # first=-2 → end=length-2
                return list(range(end))

        if self.settings.last is not None:
            if self.settings.last > 0:
                # Positive: last N elements
                start_rank = max(0, n_entities - self.settings.last)
                return list(range(start_rank, n_entities))
            else:
                # Negative: all except first |N| elements
                start_rank = min(
                    abs(self.settings.last), n_entities
                )  # last=-3 → start=3
                return list(range(start_rank, n_entities))

        # For start/end/ranks in relative mode
        if self.settings.relative:
            if relative_ranks is None:
                raise ValueError(
                    "relative_ranks parameter required for relative mode with start/end/ranks"
                )
            return self._compute_relative_ranks(relative_ranks, sequence_id)

        # Absolute mode: start/end/ranks
        return self._compute_absolute_ranks(n_entities, sequence_id)

    def _compute_absolute_ranks(self, n_entities, sequence_id=None):
        """
        Compute ranks for absolute mode (start/end/step/ranks parameters).

        Supports Python-style negative indexing and step sampling:
        - Negative indices are resolved relative to sequence length
        - step parameter enables sub-sampling (step >= 1, forward only)
        - Invalid slices (e.g., start >= end) return empty list (permissive)

        Args:
            n_entities: Total number of entities
            sequence_id: Optional sequence ID for logging

        Returns:
            List of integer positions to keep
        """
        if (
            self.settings.start is not None
            or self.settings.end is not None
            or self.settings.step is not None
        ):
            # Resolve step, start, and end with proper defaults
            step = self.settings.step if self.settings.step is not None else 1
            start = self.settings.start if self.settings.start is not None else 0
            end = self.settings.end if self.settings.end is not None else n_entities

            # Resolve negative indices
            start = self._resolve_negative_index(start, n_entities)
            end = self._resolve_negative_index(end, n_entities)

            # Python permissive behavior: range() handles invalid slices gracefully
            # Returns empty if start >= end
            return list(range(start, end, step))

        if self.settings.ranks is not None:
            # Resolve negative ranks
            resolved_ranks = [
                self._resolve_negative_index(r, n_entities) for r in self.settings.ranks
            ]

            # Filter ranks that are still in bounds after resolution
            valid_ranks = [r for r in resolved_ranks if 0 <= r < n_entities]

            if len(valid_ranks) < len(self.settings.ranks):
                LOGGER.warning(
                    "Some ranks out of bounds for sequence %s (n_entities=%d)",
                    sequence_id,
                    n_entities,
                )
            return sorted(set(valid_ranks))  # Remove duplicates and sort

        return list(range(n_entities))

    def _compute_relative_ranks(self, relative_ranks, sequence_id=None):
        """
        Compute which indices to keep based on relative ranks.

        Note: first/last are handled in absolute mode path (optimization).
        This method only handles start/end/step/ranks parameters.

        Args:
            relative_ranks: Series of relative rank values
            sequence_id: Optional sequence ID for logging

        Returns:
            List of indices to keep
        """
        if (
            self.settings.start is not None
            or self.settings.end is not None
            or self.settings.step is not None
        ):
            # Keep entities in relative rank range [start, end) with step
            step = self.settings.step if self.settings.step is not None else 1

            # Default start/end for forward step
            start = (
                self.settings.start
                if self.settings.start is not None
                else relative_ranks.min()
            )
            end = (
                self.settings.end
                if self.settings.end is not None
                else relative_ranks.max() + 1
            )

            # Generate target ranks with step
            target_ranks = list(range(start, end, step))

            # Find positions where relative rank matches target ranks
            mask = relative_ranks.isin(target_ranks)
            positions = np.where(mask.values)[0].tolist()

            if len(positions) < len(target_ranks):
                LOGGER.debug(
                    "Only %d/%d relative ranks found in sequence %s (some ranks not present)",
                    len(positions),
                    len(target_ranks),
                    sequence_id,
                )

            return positions

        if self.settings.ranks is not None:
            # Keep entities with specific relative ranks
            mask = relative_ranks.isin(self.settings.ranks)
            # Get integer positions from boolean mask
            positions = np.where(mask.values)[0].tolist()

            if len(positions) < len(self.settings.ranks):
                LOGGER.warning(
                    "Some relative ranks not found in sequence %s",
                    sequence_id,
                )
            return positions

        # No filtering specified
        return list(range(len(relative_ranks)))

    def _filter_entities_on_sequence(self, sequence, inplace=False):
        """
        Filter entities in a single sequence based on rank criterion.

        Args:
            sequence: The sequence to filter entities from
            inplace: If True, modifies the input sequence in place

        Returns:
            Filtered sequence (or None if inplace=True)
        """
        data = sequence.sequence_data
        n_entities = len(data)

        # Get relative ranks if needed (optimization via _needs_relative_ranks)
        relative_ranks = None
        if self._needs_relative_ranks():
            relative_ranks = self._get_relative_ranks(sequence)

        # Compute which indices to keep
        ranks_to_keep = self._compute_ranks_to_keep(
            n_entities, sequence.id_value, relative_ranks=relative_ranks
        )

        # Filter and return
        filtered_data = data.iloc[ranks_to_keep]
        return self._update_sequence_with_filtered_data(
            sequence, filtered_data, inplace
        )

    def _filter_entities_on_pool(self, sequence_pool, inplace=False):
        """
        Filter entities in a sequence pool based on rank criterion.

        Args:
            sequence_pool: The sequence pool to filter entities from
            inplace: If True, modifies the input pool in place

        Returns:
            Filtered sequence pool (or None if inplace=True)
        """
        data = sequence_pool.sequence_data
        id_column = sequence_pool.settings.id_column

        # Get relative ranks if needed
        relative_ranks_all = None
        if self._needs_relative_ranks():
            relative_ranks_all = self._get_relative_ranks(sequence_pool)
            # Reset index once for efficient positional access
            relative_ranks_all = relative_ranks_all.reset_index(drop=True)

        # Group by sequence ID and filter each group
        filtered_groups = []
        cumulative_position = 0  # Track position in concatenated data

        for sequence_id, group_data in data.groupby(id_column, sort=False):
            n_entities = len(group_data)

            # Extract relative ranks for this group (if needed)
            group_relative_ranks = None
            if relative_ranks_all is not None:
                # Use cumulative position instead of searching index
                group_relative_ranks = relative_ranks_all.iloc[
                    cumulative_position : cumulative_position + n_entities
                ].reset_index(drop=True)
                cumulative_position += n_entities

            # Compute ranks to keep
            ranks_to_keep = self._compute_ranks_to_keep(
                n_entities, sequence_id, relative_ranks=group_relative_ranks
            )

            # Filter and append
            if ranks_to_keep:
                filtered_groups.append(group_data.iloc[ranks_to_keep])

        # Concatenate or return empty
        if filtered_groups:
            filtered_data = pd.concat(filtered_groups)
        else:
            filtered_data = data.iloc[0:0]

        return self._update_pool_with_filtered_data(
            sequence_pool, filtered_data, inplace
        )
