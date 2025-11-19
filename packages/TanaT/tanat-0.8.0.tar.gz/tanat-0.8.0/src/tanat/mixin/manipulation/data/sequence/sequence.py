#!/usr/bin/env python3
"""
Sequence data access mixin.
"""

import logging

import pandas as pd
from pypassist.mixin.cachable import Cachable

from .....loader.base import Loader
from ..utils import (
    validate_columns,
    apply_columns,
    get_columns_to_validate,
    validate_ids,
    export_data_to_csv,
    get_empty_dataframe_like,
)
from ..exceptions import SequenceDataError
from .transform.base import SequenceDataTransformer

LOGGER = logging.getLogger(__name__)


class SequenceDataMixin:
    """
    Mixin for sequence data access and manipulation.
    """

    def __init__(self, sequence_data):
        """
        Initialize the sequence data mixin.

        Args:
            sequence_data: The sequence data (DataFrame or Loader).
        """
        self._check_sequence_data(sequence_data)
        self._sequence_data = sequence_data

        ## -- transformer
        self._transformer_base_class = SequenceDataTransformer
        self._transformer_instance = None

    @property
    def _transformer(self):
        """
        Internal property to access the correct sequence data transformer type.
        """
        if self._transformer_instance is None:
            sequence_type = self.get_registration_name()
            self._transformer_instance = SequenceDataTransformer.init(
                sequence_type, self
            )
        return self._transformer_instance

    @property
    def transformer_settings(self):
        """
        Get the settings of the sequence data transformer.
        """
        return self._transformer.settings

    def _reset_transformer(self):
        """Reset the transformer instance."""
        self._transformer_instance = None

    def _check_sequence_data(self, data):
        """
        Check the input data.
        """
        if not isinstance(data, (pd.DataFrame, Loader)):
            raise SequenceDataError(
                f"Invalid sequence data type: expected DataFrame or Loader instance, "
                f"got {type(data).__name__}."
            )

    def _get_sequence_data(self):
        """
        The sequence data with conversions applied.
        Enhanced to handle interval middle anchor sorting.
        """
        raw_data = self._get_raw_sequence_data()
        if raw_data is None:
            return None

        cols = self.settings.get_sequence_data_columns(standardize=False)
        ## Validate columns
        id_col = self.settings.id_column
        cols2validate = get_columns_to_validate(raw_data, cols, id_col)
        validate_columns(raw_data.columns, cols2validate, error_type=SequenceDataError)

        # Prepare (coercion + metadata temporal decision + granularity validation)
        prepared = self._prepare_sequence_dataframe(raw_data)

        ## Handle interval middle anchor as special case
        sequence_type = self.get_registration_name()
        if (
            sequence_type == "interval"
            and str(self.settings.anchor).lower() == "middle"
        ):
            return self._apply_middle_anchor_sorting(prepared, cols, id_col)

        ## Standard processing for all other cases
        sorting_cols = self._get_sorting_columns(prepared)
        data = apply_columns(prepared, cols, id_col, sorting_cols)
        return data

    def _apply_middle_anchor_sorting(self, raw_data, cols, id_col):
        """
        Apply middle anchor sorting for intervals.

        Process:
        1. Add temporary middle column
        2. Apply indexing and sorting
        3. Remove temporary column
        """
        temporal_cols = self.settings.temporal_columns()
        start_col, end_col = temporal_cols[0], temporal_cols[1]

        # Vérifier que les colonnes existent
        if start_col not in raw_data.columns or end_col not in raw_data.columns:
            LOGGER.warning(
                "Missing temporal columns for middle anchor sorting: %s, %s",
                start_col,
                end_col,
            )
            return apply_columns(
                raw_data,
                cols,
                id_col,
                [start_col] if start_col in raw_data.columns else [],
            )

        # Create copy with middle column
        data_with_middle = raw_data.copy()
        middle_col = "__TEMP_MIDDLE__"
        data_with_middle[middle_col] = (
            data_with_middle[start_col]
            + (data_with_middle[end_col] - data_with_middle[start_col]) / 2
        )

        # Apply indexing and sorting with middle column
        sorted_data = apply_columns(data_with_middle, cols, id_col, [middle_col])

        # Remove temporary column - only if it exists in final data
        if middle_col in sorted_data.columns:
            sorted_data = sorted_data.drop(columns=[middle_col])

        return sorted_data

    def _get_raw_sequence_data(self):
        """
        Get the raw sequence data without any column filtering or conversion.
        """
        data = self._sequence_data
        if isinstance(data, Loader):
            data = data.load()
            self._sequence_data = data
        return data

    @Cachable.caching_property
    def sequence_data(self):
        """
        The sequence data.
        """
        data = self._get_sequence_data()

        if self._is_pool:
            return data

        ## -- unique sequence
        if self.id_value not in data.index:
            return data.iloc[0:0]  # Empty DataFrame with same columns/index structure

        return data.loc[[self.id_value]]

    def export_sequence_data(
        self,
        filepath="sequence_data.csv",
        sep=",",
        exist_ok=False,
        makedirs=False,
        **kwargs,
    ):
        """
        Export sequence data to a CSV file.

        Saves the current sequence data to a CSV file with customizable
        format options.

        Args:
            filepath (str): Path for the exported CSV file.
                Can be absolute or relative path.
            sep (str): Column separator character for CSV format.
            exist_ok (bool): Whether to overwrite existing files.
                If False, raises error if file exists.
            makedirs (bool): Whether to create parent directories.
                If True, creates missing directories in path.
            **kwargs: Additional arguments passed to pandas.to_csv().
                Common options: index=False, encoding='utf-8'

        Returns:
            pd.DataFrame: The exported sequence data (copy of original).

        Examples:
            >>> # Basic export to CSV
            >>> pool.export_sequence_data("my_sequences.csv")

            >>> # Export with custom separator and directory creation
            >>> pool.export_sequence_data(
            ...     filepath="data/sequences.tsv",
            ...     sep="\\t",
            ...     makedirs=True
            ... )

            >>> # Overwrite existing file with no index
            >>> pool.export_sequence_data(
            ...     "sequences.csv",
            ...     exist_ok=True,
            ...     index=False
            ... )
        """
        return export_data_to_csv(
            self.sequence_data,
            filepath=filepath,
            sep=sep,
            exist_ok=exist_ok,
            makedirs=makedirs,
            class_name=self.__class__.__name__,
            **kwargs,
        )

    def _get_sorting_columns(self, data):
        """
        Get columns to sort by based on sequence type and anchor configuration.

        Args:
            data: DataFrame to sort

        Returns:
            list: Columns to sort by
        """
        sequence_type = self.get_registration_name()

        if sequence_type == "event":
            return self._get_event_sorting_columns(data)
        if sequence_type == "state":
            return self._get_state_sorting_columns(data)

        # Interval sequences
        return self._get_interval_sorting_columns(data)

    def _get_event_sorting_columns(self, data):
        """Get sorting columns for event sequences."""
        time_col = self.settings.time_column
        if time_col and time_col in data.columns:
            return [time_col]
        return []

    def _get_state_sorting_columns(self, data):
        """Get sorting columns for state sequences."""
        temporal_cols = self.settings.temporal_columns()
        if temporal_cols and temporal_cols[0] in data.columns:
            return [temporal_cols[0]]  # Always sort by start time
        return []

    def _get_interval_sorting_columns(self, data):
        """Get sorting columns for intervals based on anchor configuration."""
        anchor = str(self.settings.anchor).lower()  # Convert enum to lowercase string
        temporal_cols = self.settings.temporal_columns()

        if not temporal_cols:
            return []

        start_col = temporal_cols[0]
        end_col = temporal_cols[1] if len(temporal_cols) > 1 else None

        if anchor == "start":
            return [start_col] if start_col in data.columns else []
        if anchor == "end":
            return [end_col] if end_col and end_col in data.columns else []

        # Middle anchor case
        # Return empty - middle anchor needs special processing
        return []

    def _get_standardized_data(self, drop_na=False, entity_features=None):
        """
        Returns a standardized copy of the sequence data.

        Args:
            drop_na (bool): Whether to drop rows with NA values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Standardized sequence data
        """
        data_copy = self._transformer.to_standardized_data(
            drop_na, entity_features=entity_features
        ).copy()
        return data_copy

    def _get_empty_sequence_data(self):
        """Return an empty DataFrame with the same structure as sequence_data."""
        return get_empty_dataframe_like(self.sequence_data)

    def _subset_sequence_data(self, id_values):
        """
        Subset sequence data based on id values list
        """
        if self.sequence_data is None:
            return None

        valid_seq_ids = validate_ids(
            id_values, self.sequence_data.index, "sequence_data"
        )

        if not valid_seq_ids:
            LOGGER.warning(
                "No valid IDs found in sequence data. Returning empty sequence data."
            )
            return self._get_empty_sequence_data()

        return self.sequence_data.loc[valid_seq_ids]

    def to_relative_time(
        self,
        granularity,
        drop_na=False,
        entity_features=None,
    ):
        """
        Convert sequence data to relative time based on t_zero.

        Transforms temporal data to relative time units by calculating duration
        between t_zero and each entity's temporal information.

        Args:
            granularity (str): Time unit ("day", "hour", "month", etc.).
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list, optional): Features to include.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with relative time values instead of
                original temporal columns.

        Examples:
            >>> # Set reference point and convert to days
            >>> seqpool.zero_from_position(0)
            >>> relative_data = seqpool.to_relative_time("day"))
        """
        self._safe_granularity_update(granularity)

        return self._transformer.to_relative_time(
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_relative_rank(
        self,
        drop_na=False,
        rank_column=None,
        entity_features=None,
    ):
        """
        Convert sequence data to relative rank based on t_zero.

        Transforms temporal data to relative rank by calculating the rank of
        each entity's temporal information relative to t_zero.

        Args:
            drop_na (bool): Whether to drop rows with missing values.
            rank_column (str, optional): Column name for relative rank values.
                If None, uses default (__RELATIVE_RANK__).
            entity_features (list, optional): Features to include.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with relative rank values (integers).
                Rank 0 corresponds to t_zero position.

        Examples:
            >>> # Set reference and get ranks
            >>> seqpool.zero_from_position(0)
            >>> rank_data = seqpool.to_relative_rank()

            >>> # Custom rank column name
            >>> seqpool.to_relative_rank(rank_column="position_from_t0")
        """
        if rank_column is not None:
            self._transformer.update_settings(relative_rank_column=rank_column)

        return self._transformer.to_relative_rank(
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def _safe_granularity_update(self, granularity):
        """
        Safely update granularity in metadata & check type with pydantic dataclass.
        This method use the setter from the metadata mixin.

        Args:
            granularity (str): New granularity value

        Returns:
            None
        """
        self.granularity = granularity  # pylint: disable=W0201

    def to_occurrence(
        self,
        by_id=False,
        drop_na=False,
        occurrence_column=None,
        entity_features=None,
    ):
        """
        Count occurrences of vocabulary elements defined by entity_features.

        Args:
            by_id (bool): Whether to group by the id column.
                If True, counts per individual. If False, counts globally.
            drop_na (bool): Whether to drop rows with missing values.
            occurrence_column (str, optional): Name for occurrence column.
                If None, uses default (__OCCURRENCE__).
            entity_features (list, optional): List of entity features to count.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with occurrence counts.

        Examples:
            >>> # Global occurrence counts
            >>> seqpool.to_occurrence()

            >>> # Occurrence counts per individual
            >>> seqpool.to_occurrence(by_id=True)

            >>> # Custom column name
            >>> seqpool.to_occurrence(occurrence_column="count")
        """
        if occurrence_column:
            self._transformer.update_settings(occurrence_column=occurrence_column)

        return self._transformer.to_occurrence(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_time_spent(
        self,
        by_id=False,
        granularity="day",
        proportion=False,
        drop_na=False,
        time_column=None,
        entity_features=None,
    ):
        """
        Compute total time spent in each entity feature.

        Args:
            by_id (bool): If True, calculates per individual.
                If False, aggregates across entire dataset.
            granularity (str): Time unit for calculation ("day", "hour", etc.).
            proportion (bool): If True, returns proportions of total time.
            drop_na (bool): Whether to drop rows with missing values.
            time_column (str, optional): Name for time spent column.
                If None, uses default (__TIME_SPENT__).
            entity_features (list, optional): Features to calculate time for.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with time spent values.

        Examples:
            >>> # Total time spent globally in days
            >>> seqpool.to_time_spent(granularity="day")

            >>> # Time spent per individual in hours
            >>> seqpool.to_time_spent(by_id=True, granularity="hour")

            >>> # Time spent as proportions
            >>> seqpool.to_time_spent(proportion=True)
        """
        if time_column:
            self._transformer.update_settings(time_spent_column=time_column)

        return self._transformer.to_time_spent(
            by_id=by_id,
            granularity=granularity,
            proportion=proportion,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_occurrence_frequency(
        self,
        by_id=False,
        drop_na=False,
        frequency_column=None,
        entity_features=None,
    ):
        """
        Calculate occurrence frequency (proportion of total occurrences).

        Args:
            by_id (bool): If True, calculates frequency per individual.
                If False, calculates frequency across entire dataset.
            drop_na (bool): Whether to drop rows with missing values.
            frequency_column (str, optional): Name for frequency column.
                If None, uses default (__OCCURRENCE_FREQUENCY__).
            entity_features (list, optional): Features to calculate frequency for.
                If None, uses all features from sequence settings.

        Returns:
            pd.DataFrame: DataFrame with occurrence frequency values (0-1).

        Examples:
            >>> # Global occurrence frequencies
            >>> seqpool.to_occurrence_frequency()

            >>> # Occurrence frequencies per individual
            >>> seqpool.to_occurrence_frequency(by_id=True)
        """
        if frequency_column:
            self._transformer.update_settings(frequency_column=frequency_column)

        return self._transformer.to_occurrence_frequency(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_time_proportion(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        proportion_column=None,
        entity_features=None,
    ):
        """
        Convert sequence data to time proportion format.

        Calculates the proportion of time spent on different activities
        within each time unit. Useful for understanding activity patterns
        over time periods.

        Args:
            by_id (bool): Whether to group results by entity ID.
                If True, calculates proportions per entity.
                If False, aggregates across all entities.
            granularity (str): Time granularity ("day", "hour", "week", etc.).
            drop_na (bool): Whether to drop rows with missing values.
            proportion_column (str, optional): Name for proportion values column.
                If None, uses default (__TIME_PROPORTION__).
            entity_features (list, optional): Features to analyze.
                If None, uses features from sequence settings.

        Returns:
            pd.DataFrame: Time proportion data with columns:
                - time_period: temporal periods
                - proportion_column: proportion values (0-1)
                - Additional columns based on grouping and features

        Examples:
            >>> # Daily time proportions per entity
            >>> state_pool.to_time_proportion(by_id=True, granularity="day")

            >>> # Weekly aggregated proportions across all entities
            >>> interval_pool.to_time_proportion(by_id=False,
            ...                                  granularity="week")

            >>> # Monthly proportions with custom column name
            >>> state_pool.to_time_proportion(
            ...     granularity="month",
            ...     proportion_column="monthly_proportion"
            ... )
        """
        if proportion_column:
            self._transformer.update_settings(proportion_column=proportion_column)

        return self._transformer.to_time_proportion(
            by_id=by_id,
            granularity=granularity,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        distribution_column=None,
        entity_features=None,
    ):
        """
        Convert state sequence data to temporal distribution format.

        Creates temporal grid and calculates distribution of states within
        each time period. Only supported for state sequences.

        Args:
            granularity (str): Time granularity ("day", "hour", "week", etc.).
            mode (str): Distribution calculation mode:
                - 'proportion': Values as proportion (0-1)
                - 'percentage': Values as percentage (0-100)
                - 'count': Raw counts
            time_relative (bool): Whether to use relative time.
            drop_na (bool): Whether to drop rows with missing values.
            distribution_column (str, optional): Name for distribution column.
                If None, uses default (__DISTRIBUTION__).
            entity_features (list, optional): Features to analyze.
                If None, uses features from sequence settings.

        Returns:
            pd.DataFrame: Long format with columns:
                - time_period: temporal periods
                - annotation: state names
                - distribution_column: distribution values

        Raises:
            NotImplementedError: If called on non-state sequence types.

        Examples:
            >>> # Daily state proportions
            >>> state_pool.to_distribution(granularity='day', mode='proportion')

            >>> # Weekly state percentages
            >>> state_pool.to_distribution(granularity='week', mode='percentage')

            >>> # Relative time distribution
            >>> state_pool.zero_from_position(0)
            >>> state_pool.to_distribution(time_relative=True, mode='count')
        """
        if distribution_column:
            self._transformer.update_settings(distribution_column=distribution_column)

        return self._transformer.to_distribution(
            granularity=granularity,
            mode=mode,
            time_relative=time_relative,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    def as_event(
        self,
        *,
        anchor="start",
        time_column="time",
        add_duration_feature=False,
        duration_column="duration",
    ):
        """
        Convert sequence to event representation.

        Events represent instantaneous time points. For period-based sequences
        (intervals and states), this conversion extracts a single timestamp
        based on the anchor parameter.

        Args:
            anchor: Which timestamp to extract for period-based sequences.
                   - "start": Use the start time (default)
                   - "end": Use the end time
                   - "middle": Use the midpoint (intervals only)
                    Ignored for EventSequence (returns self).

            time_column: Name for the time column in the resulting EventSequence.
                        Allows custom column naming.
                        Ignored for EventSequence (returns self).

            add_duration_feature: Whether to add a duration feature when converting
                from period-based sequences (IntervalSequence or StateSequence).
                If True, computes duration (end - start) and adds it as an entity
                feature with proper duration metadata.
                Default: False.
                Ignored for EventSequence (returns self).

            duration_column: Name for the duration feature column when
                add_duration_feature=True.
                Default: "duration".
                Ignored if add_duration_feature=False or for EventSequence.

        Returns:
            EventSequence: The converted sequence.

        Examples:
            >>> # Convert interval to events using start times
            >>> events = interval_seq.as_event()
            >>> events = interval_seq.as_event(anchor="start")

            >>> # Convert using end times
            >>> events = interval_seq.as_event(anchor="end")

            >>> # Convert and add duration feature
            >>> events = interval_seq.as_event(
            ...     anchor="start",
            ...     add_duration_feature=True,
            ...     duration_column="stay_duration"
            ... )

            >>> # Custom time column name
            >>> events = state_seq.as_event(anchor="start", time_column="timestamp")

            >>> # Calling on EventSequence returns self (no copy)
            >>> same_events = event_seq.as_event()
            >>> assert same_events is event_seq

        Note:
            Duration information is lost during conversion from period-based
            sequences unless add_duration_feature=True.

        See Also:
            as_state: Convert to state sequence
            as_interval: Convert to interval sequence
        """
        return self._transformer.as_event(
            anchor=anchor,
            time_column=time_column,
            add_duration_feature=add_duration_feature,
            duration_column=duration_column,
        )

    def as_state(self, *, end_value=None, start_column="start", end_column="end"):
        """
        Convert sequence to state representation.

        States represent continuous periods where each state's end is defined
        by the start of the next state.

        Args:
            end_value: Value for the final state when converting from EventSequence.
                    Can be:
                    - None: Last event is dropped (no end boundary, default)
                    - datetime: Specific end time (e.g., datetime(2099, 12, 31))
                    - int: Numeric sentinel value
                    Ignored for StateSequence (returns self) and IntervalSequence (raises).

            start_column: Name for the start column in the resulting StateSequence.
                        Allows custom column naming.
                        Ignored for StateSequence (returns self).

            end_column: Name for the end column in the resulting StateSequence.
                        Allows custom column naming.
                        Ignored for StateSequence (returns self).

        Returns:
            StateSequence: The converted sequence.

        Raises:
            NotImplementedError: For IntervalSequence → StateSequence
                                which is not supported.

        Examples:
            >>> # Convert events to states with end value for last state
            >>> states = event_seq.as_state(end_value=datetime(2099, 12, 31))

            >>> # Calling on StateSequence returns self (no copy)
            >>> same_states = state_seq.as_state()
            >>> assert same_states is state_seq

            >>> # Custom column names
            >>> states = event_seq.as_state(
            ...     end_value=datetime(2099, 12, 31),
            ...     start_column="admission_date",
            ...     end_column="discharge_date"
            ... )

        Note:
            From EventSequence: Each state spans from its event timestamp to
            the next event's timestamp. If end_value is provided, the last event
            is converted to a state ending at end_value. Otherwise, it is dropped.

        See Also:
            as_event: Convert to event sequence
            as_interval: Convert to interval sequence
        """
        return self._transformer.as_state(
            end_value=end_value, start_column=start_column, end_column=end_column
        )

    def as_interval(
        self,
        *,
        duration=None,
        start_column="start",
        end_column="end",
        drop_duration_feature=False,
    ):
        """
        Convert sequence to interval representation.

        Intervals represent periods with explicit start and end times.
        For EventSequence, a duration must be provided.

        Args:
            duration: Required for EventSequence conversion. Can be:
                - timedelta/DateOffset: Fixed duration for all events
                - int/float: Fixed numeric duration (for timestep-based sequences)
                - str: Column name (must be entity feature with duration metadata)
                - pd.Series: Duration values (must match data length)
                Ignored for StateSequence and IntervalSequence (returns self).

            start_column: Name for the start column in the resulting IntervalSequence.
                        Allows custom column naming.
                        Ignored for IntervalSequence (returns self).

            end_column: Name for the end column in the resulting IntervalSequence.
                    Allows custom column naming.
                    Ignored for IntervalSequence (returns self).

            drop_duration_feature: Whether to drop the duration feature after conversion.
                Only applies when duration is a string (feature name).
                If True, the duration feature is removed from the resulting sequence.
                Default: False.

        Returns:
            IntervalSequence or IntervalSequencePool: The converted sequence.

        Raises:
            NotImplementedError: If duration is None for EventSequence.
            ValueError: If duration column not found, not properly configured,
                       or Series length mismatch.

        Examples:
            >>> # Fixed timedelta duration
            >>> intervals = events.as_interval(duration=timedelta(hours=8))

            >>> # Fixed DateOffset duration (calendar-aware)
            >>> intervals = events.as_interval(duration=pd.DateOffset(months=3))

            >>> # Fixed numeric duration (timestep-based)
            >>> intervals = events.as_interval(duration=5.5)

            >>> # Duration from entity feature column (already coerced by metadata)
            >>> intervals = events.as_interval(duration="duration_days")
            >>> # Note: Column must be declared as entity feature with duration metadata

            >>> # Duration from feature, then drop it
            >>> intervals = events.as_interval(
            ...     duration="duration_days",
            ...     drop_duration_feature=True
            ... )

            >>> # Duration from external Series
            >>> durations = pd.Series([5.5, 4.5, 3.0])  # Must match data length
            >>> intervals = events.as_interval(duration=durations)

            >>> # StateSequence → IntervalSequence (trivial conversion)
            >>> intervals = states.as_interval()

            >>> # Custom column names
            >>> intervals = states.as_interval(
            ...     start_column="admission_date",
            ...     end_column="discharge_date"
            ... )

        Note:
            - For EventSequence: Duration column is validated (must be entity feature
              with duration metadata). Data is already coerced by DurationFeatureCoercer.
            - StateSequence and IntervalSequence have the same structure,
              so conversion is trivial.
            - Supports calendar-aware (MONTH/YEAR), fixed (HOUR/DAY/WEEK),
              and timestep-based (UNIT) durations.

        See Also:
            as_event: Convert to event sequence
            as_state: Convert to state sequence
        """
        return self._transformer.as_interval(
            duration=duration,
            start_column=start_column,
            end_column=end_column,
            drop_duration_feature=drop_duration_feature,
        )

    def add_entity_feature(self, feature_name, values, metadata=None, override=False):
        """
        Add a new entity feature column with proper metadata.

        Creates a new feature column in the sequence data and registers it
        with appropriate metadata. The feature is automatically added to the
        entity_features list in settings.

        Args:
            feature_name (str): Name for the new feature column.
            values (pd.Series or array-like): Values for the new feature.
                Must have same length as sequence data.
            metadata (dict, optional): Metadata configuration for the feature.
                Can contain:
                - feature_type: 'categorical', 'numerical', 'textual', 'duration'
                - settings: Type-specific settings (dict or settings object)
                - Additional kwargs for settings
                If None, metadata will be inferred from values.
            override (bool): Whether to override existing feature if it exists.
                If False and feature exists, raises ValueError.

        Returns:
            self: For method chaining.

        Raises:
            ValueError: If feature_name already exists or values length mismatch.

        Examples:
            >>> # Add categorical feature (inferred)
            >>> pool.add_entity_feature("severity", ["high", "low", "medium"])

            >>> # Add duration feature with explicit metadata
            >>> from tanat.time.granularity import Granularity
            >>> pool.add_entity_feature(
            ...     "stay_duration",
            ...     [5, 10, 3],
            ...     metadata={"feature_type": "duration",
            ...              "settings": {"granularity": Granularity.DAY}}
            ... )

            >>> # Add numerical feature
            >>> pool.add_entity_feature(
            ...     "temperature",
            ...     [37.5, 38.2, 36.9],
            ...     metadata={"feature_type": "numerical"}
            ... )
        """
        # Check if feature already exists
        if feature_name in self.settings.entity_features and not override:
            raise ValueError(
                f"Feature '{feature_name}' already exists. "
                "Use override=True to replace it."
            )

        # Validate values length
        if len(values) != len(self.sequence_data):
            raise ValueError(
                f"Length of values ({len(values)}) does not match "
                f"sequence data length ({len(self.sequence_data)})."
            )

        # Add feature column to sequence data
        self._sequence_data[feature_name] = values

        # Update settings to include new entity feature (avoid duplicates)
        if feature_name not in self.settings.entity_features:
            updated_entity_features = self.settings.entity_features + [feature_name]
            self.update_settings(entity_features=updated_entity_features)

        if override and feature_name in self._metadata.entity_descriptors:
            del self._metadata.entity_descriptors[feature_name]

        # Infer missing metadata
        self._metadata = self._infer_metadata(self._metadata)

        # Apply explicit metadata if provided
        if metadata is not None:
            self.update_entity_metadata(
                feature_name,
                feature_type=metadata.get("feature_type"),
                settings=metadata.get("settings"),
            )

        # Clear caches
        self.clear_cache()
        return self

    def drop_entity_feature(self, feature_name):
        """
        Remove an entity feature column and clean up associated metadata.

        Removes the feature from sequence data, metadata, and settings.

        Args:
            feature_name (str): Name of the feature to remove.

        Returns:
            self: For method chaining.

        Examples:
            >>> # Remove a feature
            >>> pool.drop_entity_feature("duration_days")
        """
        # Validate feature exists
        if feature_name not in self.settings.entity_features:
            raise ValueError(
                f"Feature '{feature_name}' not found in entity features. "
                f"Available features: {self.settings.entity_features}"
            )

        remaining_features = [
            f for f in self.settings.entity_features if f != feature_name
        ]
        if not remaining_features:
            raise ValueError(
                "Cannot drop the last entity feature. "
                "At least one entity feature must remain."
            )

        # Column automatically excluded via sequence_data property
        self.update_settings(entity_features=remaining_features)

        # Remove metadata entry
        del self._metadata.entity_descriptors[feature_name]

        # Clear caches
        self.clear_cache()
        return self
