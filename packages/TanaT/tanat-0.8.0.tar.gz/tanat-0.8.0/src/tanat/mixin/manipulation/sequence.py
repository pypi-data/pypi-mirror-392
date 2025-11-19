#!/usr/bin/env python3
"""
Manipulation mixin for Sequence and SequencePool objects.
"""

import logging

from .base import BaseManipulationMixin
from .data.static import StaticDataMixin
from .data.sequence.sequence import SequenceDataMixin
from .metadata.sequence import SequenceMetadataMixin
from ...time.anchor import DateAnchor
from ..description.sequence import SequenceDescriptor

LOGGER = logging.getLogger(__name__)


class SequenceManipulationMixin(
    BaseManipulationMixin,
    SequenceDataMixin,
    StaticDataMixin,
    SequenceMetadataMixin,
):
    """
    Mixin providing manipulation methods for Sequence and SequencePool objects.
    Includes sequence data access, static data access, and manipulation capabilities.
    """

    # -- flag to distiguish between Trajectory/TrajectoryPool and Sequence/SequencePool
    ## -- usefull to control type when isinstance triggers a circular import
    _CONTAINER_TYPE = "sequence"

    def __init__(self, sequence_data, static_data=None, metadata=None):
        BaseManipulationMixin.__init__(self)
        SequenceDataMixin.__init__(self, sequence_data)
        StaticDataMixin.__init__(self, static_data)
        SequenceMetadataMixin.__init__(self, metadata)

        ## -- descriptor
        self._descriptor_base_class = SequenceDescriptor
        self._descriptor_instance = None

    def _get_copy_data(self, deep):
        """
        Extract data for copy operation based on sequence.

        Args:
            deep (bool): If True, create a deep copy. Default True.

        Returns:
            tuple: The extracted data to copy.
        """
        return (
            self._copy_sequence_data(deep),
            self._copy_settings(deep),
            self._copy_metadata(deep),
            self._copy_static_data(deep),
        )

    def _copy_sequence_data(self, deep):
        """Create a copy of sequence data."""
        return self.sequence_data.copy(deep=deep)

    def _create_copy_instance(self, copy_data):
        """
        Create new sequence instance with copied data.

        Args:
            copy_data (tuple): Data to copy into the new instance.

        Returns:
            Sequence or SequencePool: New instance with copied data.
        """
        sequence_data, settings, metadata, static_data = copy_data
        # pylint: disable=E1121
        if self._is_pool:
            # SequencePool case
            new_instance = self.__class__(
                sequence_data, settings, static_data, metadata
            )
        else:
            # Single sequence case
            new_instance = self.__class__(
                self.id_value,
                sequence_data,
                settings,
                static_data,
                metadata,
            )

        self._propagate_t_zero(new_instance)
        return new_instance

    def _resolve_anchor(self, anchor=None):
        """
        Resolve anchor parameter with clear type-based logic.

        Args:
            anchor (str, optional): User-provided anchor value

        Returns:
            str: Resolved anchor value
        """
        if anchor is not None:
            # return validated anchor
            return DateAnchor.from_str(anchor)

        sequence_type = self.get_registration_name()

        if sequence_type == "interval":
            # For intervals, use settings anchor
            return DateAnchor.from_str(self.settings.anchor)
        # For events and states, anchor is always 'start'
        return DateAnchor.START

    ## ----- ZEROING ----- ##

    def zero_from_position(self, position=0, anchor=None):
        """
        Set t_zero based on entity position in the sequence.

        Args:
            position (int): Position of the entity (0-based)
            anchor (DateAnchor, optional): Reference point within periods for time calculation.
                Auto-resolved by sequence type if not specified:
                - EventSequence: 'start' (events are points in time)
                - StateSequence: 'start' (beginning of state periods)
                - IntervalSequence: uses sequence settings anchor
                Override with explicit anchor for custom resolution strategy.

        Returns:
            self: For method chaining

        Examples:
            >>> # For any sequence type
            >>> seqpool.zero_from_position(1)

            >>> # For intervals with specific anchor
            >>> interval_pool.zero_from_position(1, anchor="middle")
        """
        settings_dict = {"position": position, "anchor": anchor}
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="position"
        )
        indexer.assign(self)
        return self

    def zero_from_query(self, query, use_first=True, anchor=None):
        """
        Set t_zero based on a query over sequence data.

        Args:
            query (str): Query string to filter sequence data
            use_first (bool): If True, use first matching row; if False, use last matching row
            anchor (DateAnchor, optional): Reference point within periods for time calculation.
                Auto-resolved by sequence type if not specified:
                - EventSequence: 'start' (events are points in time)
                - StateSequence: 'start' (beginning of state periods)
                - IntervalSequence: uses sequence settings anchor
                Override with explicit anchor for custom resolution strategy.

        Returns:
            self: For method chaining

        Examples:
            >>> # Query with auto-resolved anchor
            >>> seqpool.zero_from_query("feature == 'A'")

            >>> # Query with explicit anchor for intervals
            >>> interval_pool.zero_from_query("feature == 'B'", anchor="middle")

            >>> # Query with explicit anchor for states
            >>> state_pool.zero_from_query("feature == 'C'", anchor="end")
        """
        settings_dict = {"query": query, "use_first": use_first, "anchor": anchor}
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="query"
        )
        indexer.assign(self)
        return self

    ## ----- Rank-based filtering ----- ##

    def head(self, n, inplace=False):
        """
        Return the first n entities from each sequence.

        Args:
            n (int): Number of entities to return from the start of each sequence.
                If n > 0: Return first n entities
                If n < 0: Return all entities EXCEPT the last |n| entities
                If n = 0: Not allowed (raises ValueError)
            inplace (bool): If True, modifies the input sequence in place

        Returns:
            Sequence or SequencePool: New instance with the selected entities per sequence
            None if inplace=True

        Examples:
            >>> # Get first 3 entities
            >>> sequence.head(3)

            >>> # Get all entities except the last 2 (pandas-like behavior)
            >>> sequence.head(-2)

            >>> # Modify in place
            >>> sequence.head(5, inplace=True)
        """
        # Apply rank-based filtering for head
        # Note: level is implicit for Sequence, explicit for SequencePool
        filter_kwargs = {
            "criterion": {"first": n},
            "inplace": inplace,
            "criterion_type": "rank",
        }
        if self._is_pool:
            filter_kwargs["level"] = "entity"

        return self.filter(**filter_kwargs)

    def tail(self, n, inplace=False):
        """
        Return the last n entities from each sequence.

        Args:
            n (int): Number of entities to return from the end of each sequence.
                If n > 0: Return last n entities
                If n < 0: Return all entities EXCEPT the first |n| entities
                If n = 0: Not allowed (raises ValueError)
            inplace (bool): If True, modifies the input sequence in place

        Returns:
            Sequence or SequencePool: New instance with the selected entities per sequence
            None if inplace=True

        Examples:
            >>> # Get last 3 entities
            >>> sequence.tail(3)

            >>> # Get all entities except the first 2 (pandas-like behavior)
            >>> sequence.tail(-2)

            >>> # Modify in place
            >>> sequence.tail(5, inplace=True)
        """
        # Apply rank-based filtering for tail
        # Note: level is implicit for Sequence, explicit for SequencePool
        filter_kwargs = {
            "criterion": {"last": n},
            "inplace": inplace,
            "criterion_type": "rank",
        }
        if self._is_pool:
            filter_kwargs["level"] = "entity"

        return self.filter(**filter_kwargs)

    def slice(self, start=None, end=None, step=None, relative=False, inplace=False):
        """
        Select entities within a specific rank range with optional step sampling.

        Args:
            start (int, optional): Start rank (inclusive, 0-based).
                Supports negative indices in absolute mode.
            end (int, optional): End rank (exclusive, 0-based).
                Supports negative indices in absolute mode.
            step (int, optional): Step size for sampling. Default: None (equivalent to 1).
                - step > 0: Forward sampling (e.g., 2 = every 2nd element)
                - step < 0: Backward sampling (requires appropriate start/end)
                - step = 0: Not allowed (raises ValueError)
            relative (bool): If True, uses T0-relative ranks. Defaults to False.
            inplace (bool): If True, modifies the input sequence in place.

        Returns:
            Sequence or SequencePool: Filtered sequence(s) with selected entities
            None if inplace=True

        Examples:
            >>> # Absolute mode (position-based)
            >>> sequence.slice(start=10, end=50)  # Entities at positions 10-49
            >>> sequence.slice(start=-10)         # Last 10 entities
            >>> sequence.slice(end=20, step=2)    # First 20, every 2nd element

            >>> # Relative mode (T0-based temporal)
            >>> sequence.slice(start=-10, end=10, relative=True)  # ±10 around T0
            >>> sequence.slice(start=0, end=100, step=5, relative=True)  # T0 to T0+100, every 5
        """
        # Apply rank-based filtering for slicing
        # Note: level is implicit for Sequence, explicit for SequencePool
        filter_kwargs = {
            "criterion": {
                "start": start,
                "end": end,
                "step": step,
                "relative": relative,
            },
            "inplace": inplace,
            "criterion_type": "rank",
        }
        if self._is_pool:
            filter_kwargs["level"] = "entity"

        return self.filter(**filter_kwargs)

    @property
    def vocabulary(self):
        """Return the vocabulary of sequence data using settings.entity_features."""
        return self.get_vocabulary()

    def get_vocabulary(self, entity_features=None):
        """
        Return the vocabulary of sequence data for specific entity features.

        Args:
            entity_features (list, optional): List of entity features to include in the vocabulary.
                If None, self.settings.entity_features will be used.

        Returns:
            set: Unique values from the specified entity features.
        """
        if entity_features is not None:
            entity_features = self.settings.validate_and_filter_entity_features(
                entity_features
            )
        feats = (
            self.settings.entity_features
            if entity_features is None
            else entity_features
        )

        data_rows = self.sequence_data[feats].values
        if len(feats) > 1:
            return set(tuple(item) for item in data_rows)
        return set(data_rows.flatten())

    @property
    def _descriptor(self):
        """
        Internal property to access the correct sequence descriptor.
        """
        if self._descriptor_instance is None:
            sequence_type = self.get_registration_name()
            self._descriptor_instance = SequenceDescriptor.init(sequence_type, self)
        return self._descriptor_instance

    def describe(self, aggregate=False, dropna=False, add_to_static=False):
        """
        Generate a statistical description of the sequence.

        Args:
            aggregate (bool): If True, applies pandas describe() to aggregate
                statistics across all sequences in the pool. Returns summary
                statistics (count, mean, std, min, max, quartiles) for each metric.
                Only meaningful for pools with multiple sequences.
                Default: False.

            dropna (bool): If True, silently drops missing duration values (NaT).
                If False, raises ValueError when NaT values are encountered in
                duration calculations. Default: False.
                Note: For StateSequence without default_end_value, the last state
                naturally has NaT end time. Setting dropna=False will raise an
                error in this case.

            add_to_static (bool): If True, add individual descriptions to static_data.
                Ignored (with warning) if aggregate=True since aggregated statistics.
                Default: False.

        Returns:
            pd.DataFrame:
                - If aggregate=False: One row per sequence with computed metrics.
                  Index is named with settings.id_column.
                - If aggregate=True: Summary statistics (count, mean, std, etc.)
                  for each metric across all sequences.

        Raises:
            ValueError: If dropna=False and NaT values are found in temporal columns.

        Examples:
            >>> pool.describe()  # Individual sequence descriptions
            >>> pool.describe(aggregate=True)  # Aggregated statistics
            >>> pool.describe(add_to_static=True)  # Add descriptions to static_data
        """
        # return id_value for unique sequence, None for pool
        sequence_id = getattr(self, "id_value", None)

        # Compute description with properly named index
        seq_desc = self._descriptor.describe(dropna=dropna)
        result = seq_desc.to_dataframe(
            sequence_id=sequence_id, index_name=self.settings.id_column
        )

        # Add to static data if requested (only for non-aggregated)
        if add_to_static:
            if aggregate:
                LOGGER.warning(
                    "add_to_static=True ignored with aggregate=True. "
                    "Only individual descriptions can be added to static_data."
                )
            else:
                desc_features = result.columns.tolist()

                self.add_static_features(
                    static_data=result,
                    id_column=self.settings.id_column,
                    static_features=desc_features,
                    override=True,
                    metadata=seq_desc.to_metadata(),
                )

        # Return aggregated or individual descriptions
        if aggregate:
            return result.describe()

        return result

    def _reset_descriptor(self):
        """Reset the descriptor instance."""
        self._descriptor_instance = None

    def clear_cache(self):
        """
        Clear all cached data and reset the transformer.
        """
        super().clear_cache()
        self._reset_transformer()
        self._reset_descriptor()
