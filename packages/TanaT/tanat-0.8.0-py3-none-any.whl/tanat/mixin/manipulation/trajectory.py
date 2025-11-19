#!/usr/bin/env python3
"""
Manipulation mixin for Trajectory and TrajectoryPool objects.
"""

import logging

from .base import BaseManipulationMixin
from .data.static import StaticDataMixin
from .metadata.trajectory import TrajectoryMetadataMixin
from ..description.trajectory import TrajectoryDescriptor

LOGGER = logging.getLogger(__name__)


class TrajectoryManipulationMixin(
    BaseManipulationMixin,
    StaticDataMixin,
    TrajectoryMetadataMixin,
):
    """
    Mixin providing manipulation methods for Trajectory and TrajectoryPool objects.
    Includes static data access and manipulation capabilities.
    """

    # -- flag to distiguish between Trajectory/TrajectoryPool and Sequence/SequencePool
    ## -- usefull to control type when isinstance triggers a circular import
    _CONTAINER_TYPE = "trajectory"

    def __init__(self, static_data=None, metadata=None):
        BaseManipulationMixin.__init__(self)
        StaticDataMixin.__init__(self, static_data)
        TrajectoryMetadataMixin.__init__(self, metadata)

        ## -- descriptor
        self._descriptor_base_class = TrajectoryDescriptor
        self._descriptor_instance = None

    def _get_copy_data(self, deep):
        """
        Extract data for copy operation.

        Args:
            deep (bool): If True, create a deep copy. Default True.

        Returns:
            tuple: The extracted data to copy.
        """
        return (
            self._copy_sequence_pools(deep),
            self._copy_settings(deep),
            self._copy_static_data(deep),
            self._copy_metadata(deep),
        )

    def _copy_sequence_pools(self, deep):
        """Create a copy of sequence pools dict."""
        if deep:
            # Deep copy: clone each sequence pool
            return {
                name: pool.copy(deep=True)
                for name, pool in self._sequence_pools.items()
            }
        # Shallow copy: reuse sequence pool references
        return {**self._sequence_pools}

    def _create_copy_instance(self, copy_data):
        """
        Create new instance with copied data.

        Args:
            copy_data (tuple): Data to copy into the new instance.

        Returns:
            Trajectory or TrajectoryPool: New instance with copied data.
        """
        sequence_pools, settings, static_data, metadata = copy_data

        # pylint: disable=E1123
        if self._is_pool:
            # TrajectoryPool case
            new_instance = self.__class__(
                sequence_pools=sequence_pools,
                settings=settings,
                static_data=static_data,
                metadata=metadata,
            )
        else:
            # Single Trajectory case
            new_instance = self.__class__(
                id_value=self.id_value,
                sequence_pools=sequence_pools,
                static_data=static_data,
                settings=settings,
                metadata=metadata,
            )

        self._propagate_t_zero(new_instance)
        return new_instance

    def _get_sequence_pool(self, sequence_name):
        """
        Get a sequence pool by name with validation.

        Args:
            sequence_name (str): The name of the sequence pool to retrieve.

        Returns:
            SequencePool: The requested sequence pool.
        """
        seqpool = self._sequence_pools.get(sequence_name)
        if seqpool is None:
            raise ValueError(f"Sequence with name '{sequence_name}' not found.")
        return seqpool

    def _apply_filter_to_all_sequences(self, criterion, criterion_type, inplace):
        """
        Apply a filter criterion to all sequence pools.

        Args:
            criterion (dict): Filter criterion to apply
            criterion_type (str): Type of criterion (e.g., "rank")
            inplace (bool): If True, modify in place

        Returns:
            Trajectory/TrajectoryPool or None: Filtered instance or None if inplace
        """
        new_instance = None if inplace else self.copy(deep=False)

        for seq_name, seqpool in self._sequence_pools.items():
            filtered_seqpool = seqpool.filter(
                criterion=criterion,
                level="entity",
                criterion_type=criterion_type,
            )

            if inplace:
                self._sequence_pools[seq_name] = filtered_seqpool
                self.clear_cache()
            else:
                # pylint: disable=protected-access
                new_instance._sequence_pools[seq_name] = filtered_seqpool

        return None if inplace else new_instance

    def _apply_rank_filter(self, rank_params, sequence_name=None, inplace=False):
        """
        Apply a rank-based filter to a specific sequence or all sequences.

        Args:
            rank_params (dict): Rank filter parameters (e.g., {"first": 5}, {"start": 0, "end": 10})
            sequence_name (str, optional): Name of the sequence to apply the filter to.
                If None, applies to all sequences.
            inplace (bool): If True, modify in place

        Returns:
            Trajectory/TrajectoryPool or None: Filtered instance or None if inplace
        """
        if sequence_name is not None:
            # For TrajectoryPool, we need to pass level="entity"
            # For Trajectory, level is implicit
            filter_kwargs = {
                "criterion": rank_params,
                "sequence_name": sequence_name,
                "criterion_type": "rank",
                "inplace": inplace,
            }
            if self._IS_POOL:
                filter_kwargs["level"] = "entity"

            return self.filter(**filter_kwargs)

        return self._apply_filter_to_all_sequences(
            criterion=rank_params,
            criterion_type="rank",
            inplace=inplace,
        )

    ## ----- ZEROING ----- ##

    def zero_from_position(self, position=0, sequence_name=None, anchor="start"):
        """
        Set t_zero based on entity position in a specific sequence.

        Args:
            position (int): Position of the entity (0-based)
            sequence_name (str): Name of the sequence to apply indexing to.
                If None, position is applied across all sequences combined.
            anchor (str): Temporal anchor point for intervals/states.
                Options: "start", "end", "middle". Not used for event sequences.

        Returns:
            self: For method chaining

        Example:
            >>> trajectory.zero_from_position(1, sequence_name="event")
        """
        settings_dict = {
            "position": position,
            "sequence_name": sequence_name,
            "anchor": anchor,
        }
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="position"
        )
        indexer.assign(self)
        return self

    def zero_from_query(self, query, sequence_name, use_first=True, anchor="start"):
        """
        Set t_zero based on a query over a specific sequence.

        Args:
            query (str): Query string to filter sequence data
            sequence_name (str): Name of the sequence to apply query to
            use_first (bool): Use first matching row if True, last if False
            anchor (str): Temporal anchor point for intervals/states.
                Options: "start", "end", "middle". Not used for event sequences.

        Returns:
            self: For method chaining

        Example:
            >>> trajectory.zero_from_query("event_type == 'EMERGENCY'",
            ...                           sequence_name="event")
        """
        settings_dict = {
            "query": query,
            "sequence_name": sequence_name,
            "use_first": use_first,
            "anchor": anchor,
        }
        indexer = self._zeroing_base_class.init(
            settings=settings_dict, zero_setter_type="query"
        )
        indexer.assign(self)
        return self

    ## ----- Rank-based filtering ----- ##

    def head(self, n, sequence_name=None, inplace=False):
        """
        Get the first n entities from the sequence.

        Args:
            n (int): Number of entities to return from the start of each sequence.
                If n > 0: Return first n entities
                If n < 0: Return all entities EXCEPT the last |n| entities
                If n = 0: Not allowed (raises ValueError)
            sequence_name (str, optional): Name of the sequence to apply the method to.
                If None, applies to all sequences.
            inplace (bool, optional): If True, modifies the current trajectory. Defaults to False.

        Returns:
            Trajectory or TrajectoryPool: New instance containing the first n entities.
            None if inplace=True
        """
        return self._apply_rank_filter(
            rank_params={"first": n},
            sequence_name=sequence_name,
            inplace=inplace,
        )

    def tail(self, n, sequence_name=None, inplace=False):
        """
        Return the last n entities from each sequence.

        Args:
            n (int): Number of entities to return from the end of each sequence.
                If n > 0: Return last n entities
                If n < 0: Return all entities EXCEPT the first |n| entities
                If n = 0: Not allowed (raises ValueError)
            sequence_name (str, optional): Name of the sequence to apply the method to.
                If None, applies to all sequences.
            inplace (bool, optional): If True, modifies the current trajectory. Defaults to False.

        Returns:
            Trajectory or TrajectoryPool: New instance containing the last n entities.
            None if inplace=True
        """
        return self._apply_rank_filter(
            rank_params={"last": n},
            sequence_name=sequence_name,
            inplace=inplace,
        )

    def slice(self, start=None, end=None, step=None, sequence_name=None, inplace=False):
        """
        Slice entities in each sequence similar to Python slicing.

        Args:
            start (int, optional): Starting index of the slice. Defaults to None.
            end (int, optional): Ending index of the slice. Defaults to None.
            step (int, optional): Step size for sampling (must be >= 1). Defaults to None.
            sequence_name (str, optional): Name of the sequence to apply the method to.
                If None, applies to all sequences.
            inplace (bool, optional): If True, modifies the current trajectory. Defaults to False.

        Returns:
            Trajectory or TrajectoryPool: New instance containing the sliced entities.
            None if inplace=True

        Examples:
            >>> # Slice all sequences
            >>> traj.slice(start=0, end=10)

            >>> # Sub-sample every 2nd entity across all sequences
            >>> traj.slice(step=2)

            >>> # Slice specific sequence with step
            >>> traj.slice(start=5, end=20, step=3, sequence_name="event")
        """
        return self._apply_rank_filter(
            rank_params={"start": start, "end": end, "step": step},
            sequence_name=sequence_name,
            inplace=inplace,
        )

    @property
    def _descriptor(self):
        """
        Internal property to access the trajectory descriptor.
        """
        if self._descriptor_instance is None:
            self._descriptor_instance = TrajectoryDescriptor(self)
        return self._descriptor_instance

    def describe(
        self, dropna=False, aggregate=False, add_to_static=False, separator="_"
    ):
        """
        Generate a statistical description of all sequences in the trajectory.

        Concatenates descriptions from all sequence pools into a single DataFrame,
        with column names prefixed by sequence name to avoid conflicts.

        Args:
            dropna (bool): If True, silently drops NaT values in temporal columns.
                If False, raises ValueError when NaT values are encountered.
                Default: False.
            aggregate (bool): If True, return aggregated statistics across all trajectories.
                If False, return individual descriptions per trajectory.
                Default: False.
            add_to_static (bool): If True, add descriptions to static_data.
                Ignored (with warning) if aggregate=True.
                Default: False.
            separator (str): Separator to use between sequence name and metric name.
                Default: "_" (e.g., "hosp_length", "presc_entropy")

        Returns:
            pd.DataFrame: Combined description with columns prefixed by sequence name.
                - First column: n_sequences (number of sequence pools)
                - Remaining columns: {seq_name}{separator}{metric}
                - If TrajectoryPool: One row per trajectory
                - If Trajectory (single): One row for this trajectory only
                - If aggregate=True: Aggregated statistics

        Raises:
            ValueError: If dropna=False and NaT values are found in temporal columns.

        Examples:
            >>> # TrajectoryPool - describe all trajectories
            >>> trajectory_pool.describe(dropna=True)
            # Returns: DataFrame with rows for all trajectories

            >>> # Trajectory - describe single trajectory
            >>> trajectory = trajectory_pool[101]
            >>> trajectory.describe(dropna=True)
            # Returns: DataFrame with single row for trajectory 101

            >>> # Add all descriptions to static_data
            >>> trajectory_pool.describe(dropna=True, add_to_static=True)

            >>> # Aggregated statistics
            >>> trajectory_pool.describe(aggregate=True)

            >>> # Custom separator
            >>> trajectory.describe(separator=".")
            # Returns: n_sequences, hosp.length, presc.entropy, auto.n_transitions
        """
        # Compute trajectory description using descriptor
        traj_desc = self._descriptor.describe(dropna=dropna)

        # Extract trajectory_id for single trajectory (like sequence_id for Sequence)
        trajectory_id = getattr(self, "id_value", None)

        # Convert to DataFrame with proper index name
        result = traj_desc.to_dataframe(
            trajectory_id=trajectory_id,
            index_name=self.settings.id_column,
            separator=separator,
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
                    metadata=traj_desc.to_metadata(separator=separator),
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
        Clear all cached data and reset the descriptor.
        """
        super().clear_cache()
        self._reset_descriptor()
