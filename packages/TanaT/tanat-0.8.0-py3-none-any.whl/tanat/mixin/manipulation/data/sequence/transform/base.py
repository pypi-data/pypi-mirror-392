#!/usr/bin/env python3
"""
Base Transformer for sequence data.
"""

from abc import ABC, abstractmethod
import logging

from pypassist.mixin.registrable import Registrable
from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin

from .settings import TransformSettings
from .exceptions import TransformationError
from ......time.duration import calculate_duration_from_series

LOGGER = logging.getLogger(__name__)


class SequenceDataTransformer(
    ABC,
    Cachable,
    SettingsMixin,
    Registrable,
):
    """
    Interface for type-specific sequence data transformers.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"
    SETTINGS_DATACLASS = TransformSettings

    def __init__(self, sequence, settings=None):
        if settings is None:
            settings = TransformSettings()
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        self._sequence = sequence

    @classmethod
    def init(cls, transformer_type, sequence, settings=None):
        """
        Initialize the transformer for a specific type.

        Args:
            transformer_type:
                The transformer type.

            sequence:
                The sequence or sequence pool to transform.

            settings:
                Optional settings for the transformer. If not provided,
                defaults from the TransformSettings dataclass will be used.

        Returns:
            An instance of the transformer.
        """
        return cls.get_registered(transformer_type)(sequence, settings)

    @property
    def sequence_settings(self):
        """
        Get the sequence settings associated with the sequence being transformed.
        """
        return self._sequence.settings

    def _get_basic_standardized_data(self, drop_na, entity_features=None):
        """
        Basic standardized data processing for simple sequence types.
        Common pattern for event and interval sequences.
        """
        data_origin = self._sequence.sequence_data
        col2keep = self.sequence_settings.get_sequence_data_columns(
            standardize=True, entity_features=entity_features
        )

        if drop_na:
            data_copy = data_origin.copy()
            data_copy.dropna(how="any", inplace=True)
            return data_copy[col2keep]

        return data_origin[col2keep]

    @Cachable.caching_method()
    def to_standardized_data(self, drop_na=False, entity_features=None):
        """
        Returns a standardized copy of the sequence data.

        This method provides a consistent interface for getting sequence data
        that has been properly processed according to its type. Particularly,
        useful for state sequences without end column.

        Args:
            drop_na (bool): Whether to drop rows with NA values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Standardized sequence data
        """
        return self._standardized_data(drop_na, entity_features=entity_features)

    @abstractmethod
    def _standardized_data(self, drop_na, entity_features=None):
        """
        Process the data according to sequence type and return a standardized copy.

        This method should be implemented by subclasses to handle
        type-specific data processing.

        Args:
            drop_na (bool): Whether to drop rows with NA values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Processed data
        """

    def _add_t0_column(self, sequence_data_copy, t_zero, tmp_t0_col):
        """
        Set reference dates in the data for duration calculation.

        Handles both single date values and dictionaries mapping sequence IDs
        to their respective T0 dates.

        Args:
            sequence_data_copy (pd.DataFrame): Copy of sequence data
            t_zero (datetime or dict): Reference date(s) for calculation
            tmp_t0_col (str): Temporary t0 column name

        Returns:
            pd.DataFrame: Data with T0 column added
        """
        if not t_zero:
            raise TransformationError(
                "T zero cannot be empty or None. "
                "Please provide a valid T zero value to allow relative time transformation."
            )
        if isinstance(t_zero, dict):
            sequence_data_copy[tmp_t0_col] = sequence_data_copy.index.map(t_zero)
        else:
            sequence_data_copy[tmp_t0_col] = t_zero
        return sequence_data_copy

    def _cleanup_temporal_columns(self, data, columns_to_drop):
        """
        Remove temporary and original temporal columns after transformation.

        Args:
            data (pd.DataFrame): Transformed data
            columns_to_drop (list): List of columns to drop

        Returns:
            pd.DataFrame: Data with temporal columns removed
        """
        return data.drop(columns_to_drop, axis=1)

    @Cachable.caching_method()
    def to_relative_time(
        self,
        drop_na=False,
        entity_features=None,
        tmp_t0_col="__TMP_T0__",
    ):
        """
        Transform sequence data to relative time based on t_zero.

        This method converts temporal data to relative time units (days, hours, etc.)
        by calculating the duration between the t_zero and each entity's temporal
        information.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.
            tmp_t0_col (str, optional): Temporary t0 column name

        Returns:
            pd.DataFrame: Transformed data with relative time values
        """
        data = self._to_relative_time(
            drop_na,
            entity_features=entity_features,
            tmp_t0_col=tmp_t0_col,
        )

        if drop_na:  # drop Na values introduced if T0 is missing
            data.dropna(inplace=True)
        return data

    @abstractmethod
    def _to_relative_time(
        self,
        drop_na,
        entity_features=None,
        tmp_t0_col="__TMP_T0__",
    ):
        """
        Abstract method to implement relative time transformation.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.
            tmp_t0_col (str, optional): Temporary t0 column name

        Returns:
            pd.DataFrame: Transformed data with relative time values
        """

    @Cachable.caching_method()
    def to_relative_rank(
        self,
        drop_na=False,
        entity_features=None,
    ):
        """
        Convert sequence data to relative rank based on t_zero.

        This method transforms temporal data to relative rank units by calculating
        the rank of each entity's temporal information relative to the t_zero.
        The behavior varies by sequence type:

        - Event sequences: Ranks events based on their timestamps
        - Interval/State sequences: Ranks intervals/states based on the specified anchor

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: DataFrame with relative rank values
        """
        sequence_settings = self.sequence_settings
        id_col = sequence_settings.id_column
        time_col = self.settings.relative_time_column
        relative_rank_column = self.settings.relative_rank_column

        relative_df = self._standardize_relative_data(
            drop_na=drop_na,
            entity_features=entity_features,
        )

        def _compute_group_rank(group):
            """Compute relative rank for a single group (sequence)."""
            # Handle groups with no valid relative times
            if group[time_col].isnull().all():
                return group.rename(columns={time_col: relative_rank_column})

            # Sort by relative time and assign initial ranks
            group_sorted = group.sort_values(by=time_col)
            group_sorted[relative_rank_column] = range(len(group_sorted))

            # Find T0 position and adjust ranks
            t0_mask = group_sorted[time_col] == 0
            if t0_mask.any():  # More robust check
                t0_position = group_sorted.loc[t0_mask, relative_rank_column].iloc[0]
                group_sorted[relative_rank_column] -= t0_position

            # Clean up: remove temporary column
            return group_sorted.drop(columns=[time_col])

        # Apply ranking to each group
        data = relative_df.groupby(id_col, group_keys=False, observed=True).apply(
            _compute_group_rank
        )
        if drop_na:  # drop Na values introduced if T0 is missing
            data.dropna(inplace=True)
        return data

    @abstractmethod
    def _standardize_relative_data(self, drop_na=False, entity_features=None):
        """
        Abstract method to implement relative rank transformation.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: DataFrame with relative time values
        """

    @Cachable.caching_method()
    def to_occurrence(
        self,
        by_id=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Counts occurrences of vocabulary elements defined by entity_features.

        Args:
            by_id (bool): Whether to group by the id column.
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list, optional): Subset list of entity features to consider.
            If None, all entity features specified in the sequence settings will be used.

        Returns:
            pd.DataFrame: DataFrame with occurrence counts.
        """
        features = self._validate_and_filter_entity_features(entity_features)
        groupby_cols = (
            features if not by_id else [self.sequence_settings.id_column] + features
        )

        return (
            self._standardized_data(drop_na)
            .groupby(groupby_cols, observed=True, dropna=False)
            .size()
            .reset_index(name=self.settings.occurrence_column)
        )

    @Cachable.caching_method()
    def to_time_spent(
        self,
        by_id=False,
        granularity="day",
        proportion=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Computes the total time spent in each entity feature as defined by entity_features.

        Args:
            by_id (bool): If True, calculates time spent per individual (grouped by id column).
                  If False, aggregates across the entire dataset.
            granularity (str): The unit of time for calculation (e.g., "day", "hour").
            proportion (bool): If True, returns time spent as a proportion of total time.
            drop_na (bool): If True, excludes rows with missing values in entity features.
            entity_features (list, optional): List of entity features to include in the calculation.
                              If None, uses all features specified in the sequence settings.

        Returns:
            pd.DataFrame: A DataFrame showing the time spent in each entity
                         feature (and per id if by_id=True).
        """
        time_spent_df = self._to_time_spent(
            by_id, granularity, drop_na, entity_features
        )
        if not proportion:
            return time_spent_df

        return self._add_frequency_column(
            data=time_spent_df,
            value_column=self.settings.time_spent_column,
            frequency_column=self.settings.time_proportion_column,
            by_id=by_id,
        )

    @abstractmethod
    def _to_time_spent(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        entity_features=None,
    ):
        """
        Abstract method to implement time spent transformation.

        Args:
            by_id (bool): Whether to group by the id column.
            granularity (str): Granularity for time calculation (e.g., "day", "hour").
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list, optional): Subset list of entity features to consider.
                If None, all entity features specified in the sequence settings will be used.

        Returns:
            pd.DataFrame: DataFrame with time spent in each state/interval.
        """

    def _compute_time_spent_for_period_sequences(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        entity_features=None,
    ):
        """
        Compute total time spent in each entity feature for period-type sequences
        (intervals or states).

        Args:
            by_id (bool): If True, group results by the ID column.
            granularity (str): Unit of time for duration calculation (e.g., "day", "hour").
            drop_na (bool): If True, exclude rows with missing values.
            entity_features (list, optional): List of entity features to include.
            If None, uses all features from settings.

        Returns:
            pd.DataFrame: DataFrame with aggregated time spent values.
        """
        sequence_settings = self.sequence_settings
        start_col, end_col = sequence_settings.temporal_columns(standardize=True)
        time_spent_col = self.settings.time_spent_column

        data = self._standardized_data(drop_na)
        if not drop_na:  # if drop_na copy was done before
            data = data.copy()

        data[time_spent_col] = calculate_duration_from_series(
            start_series=data[start_col],
            end_series=data[end_col],
            granularity=granularity,
        )

        entity_features = self._validate_and_filter_entity_features(entity_features)
        group_by = entity_features.copy()

        if by_id:
            id_col = sequence_settings.id_column
            group_by = [id_col] + group_by
            data.reset_index(drop=False, inplace=True)

        return data.groupby(group_by, as_index=False, observed=True)[
            time_spent_col
        ].sum()

    @Cachable.caching_method()
    def to_occurrence_frequency(
        self,
        by_id=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Calculate occurrence frequency (proportion of total occurrences).

        Args:
            by_id (bool): If True, calculates frequency per individual.
                        If False, calculates frequency across entire dataset.
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list, optional): List of entity features to include.

        Returns:
            pd.DataFrame: DataFrame with occurrence frequencies (proportions).
        """
        occurrence_data = self.to_occurrence(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )
        return self._add_frequency_column(
            data=occurrence_data,
            value_column=self.settings.occurrence_column,
            frequency_column=self.settings.frequency_column,
            by_id=by_id,
        )

    def _add_frequency_column(
        self,
        data,
        value_column,
        frequency_column,
        by_id,
    ):
        """
        Helper method to add frequency column to existing data.
        Drop the value column after frequency calculation.

        Args:
            data (pd.DataFrame): Input data with values to calculate frequency from
            value_column (str): Column containing values to calculate frequency for
            frequency_column (str): Name of the new frequency column
            by_id (bool): Whether to calculate frequency per id group or globally

        Returns:
            pd.DataFrame: Data with added frequency column
        """
        result = data.copy()

        if by_id:
            # Calculate frequency per id (group)
            id_col = self.sequence_settings.id_column
            result[frequency_column] = result.groupby(id_col, observed=True)[
                value_column
            ].transform(lambda x: x / x.sum())
        else:
            # Calculate frequency across entire dataset
            total = result[value_column].sum()
            result[frequency_column] = result[value_column] / total

        # Drop the original value column
        result.drop(columns=[value_column], inplace=True)

        return result

    @Cachable.caching_method()
    def to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform sequence data to temporal distribution format.

        Args:
            mode (str): Distribution calculation mode ('proportion', 'percentage', 'count')
            time_relative (bool): Whether to use relative time for distribution
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include

        Returns:
            pd.DataFrame: Temporal distribution data in long format
        """
        return self._to_distribution(
            granularity=granularity,
            mode=mode,
            time_relative=time_relative,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    @abstractmethod
    def _to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Abstract method to implement distribution transformation.

        Args:
            mode (str): Distribution calculation mode
            time_relative (bool): Whether to use relative time
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include

        Returns:
            pd.DataFrame: Temporal distribution data
        """

    def _validate_and_filter_entity_features(
        self,
        subset_entity_features,
    ):
        """
        Validate and filter entity features with warnings for invalid ones.

        Args:
            subset_entity_features: Requested features (str, list, or None)

        Returns:
            List[str]: Filtered list of valid features
        """
        return self.sequence_settings.validate_and_filter_entity_features(
            subset_entity_features,
        )

    # --- Abstract methods for sequence conversion ---

    @abstractmethod
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

        This method must be implemented by each transformer to handle conversion
        to EventSequence.

        Args:
            anchor: Which timestamp to extract for period-based sequences.
                    - "start": Use the start time (default)
                    - "end": Use the end time
                    - "middle": Use the midpoint
            time_column: Name for the time column in the resulting EventSequence
        """

    @abstractmethod
    def as_state(self, *, end_value=None, start_column="start", end_column="end"):
        """
        Convert sequence to state representation.

        This method must be implemented by each transformer to handle conversion
        to StateSequence.

        Args:
            end_value: Value for final state (EventSequence only). Can be:
                      - None: Drop last event (default)
                      - datetime: Specific end time
                      - int: Numeric sentinel value
            start_column: Name for the start column in the resulting StateSequence
            end_column: Name for the end column in the resulting StateSequence

        """

    @abstractmethod
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

        This method must be implemented by each transformer to handle conversion
        to IntervalSequence.

        Args:
            duration: Duration specification. Can be:
                     - timedelta/DateOffset: Fixed duration for all events
                     - int/float: Fixed numeric duration (timestep-based sequences)
                     - str: Column name (must be entity feature with duration metadata)
                     - pd.Series: Duration values (must match data length)
                     Required for EventSequence, ignored for StateSequence/IntervalSequence.
            start_column: Name for the start column in the resulting IntervalSequence
            end_column: Name for the end column in the resulting IntervalSequence
        """

    # --- Helper methods for sequence conversion ---

    def _build_sequence_settings(self, **temporal_kwargs):
        """
        Build settings dict for sequence conversion.

        Constructs a settings dictionary containing id_column, entity_features,
        static_features, and type-specific temporal columns.

        Args:
            **temporal_kwargs: Temporal column names:
                - time_column: For event sequences
                - start_column, end_column: For period sequences (state/interval)
                - default_end_value: For state sequences (optional)

        Returns:
            dict: Settings dictionary for the target sequence type
        """
        sequence_settings = self.sequence_settings

        base_settings = {
            "id_column": sequence_settings.id_column,
            "entity_features": sequence_settings.entity_features,
            "static_features": sequence_settings.static_features,
        }

        # Add type-specific temporal settings
        base_settings.update(temporal_kwargs)

        return base_settings

    def _create_converted_sequence(self, stype, sequence_data, settings):
        """
        Create a new sequence of the target type (handles Pool vs Sequence).

        Uses the source sequence's class method to create the new sequence,
        automatically handling Pool vs Sequence logic through polymorphism.

        Args:
            stype: Target sequence type ('event', 'state', 'interval')
            sequence_data: DataFrame with converted data
            settings: Settings dict for the new sequence

        Returns:
            Sequence or SequencePool of the target type
        """
        # Filter metadata to only include entity features present in settings
        filtered_metadata = self._filter_metadata_for_settings(settings)

        init_kwargs = {
            "stype": stype,
            "sequence_data": sequence_data,
            "settings": settings,
            "static_data": self._sequence.static_data,
            "metadata": filtered_metadata,
        }

        # Add id_value only for single sequences (not pools)
        if not self._sequence._is_pool:  # pylint: disable=protected-access
            init_kwargs["id_value"] = self._sequence.id_value

        # Use the source sequence's class init method (polymorphic call)
        return self._sequence.__class__.init(**init_kwargs)

    def _filter_metadata_for_settings(self, settings):
        """
        Filter entity_descriptors to match entity_features in settings.

        Creates a copy of metadata with only the entity descriptors that
        correspond to entity features declared in the provided settings.

        Args:
            settings: Settings dict with 'entity_features' key

        Returns:
            SequenceMetadata: Filtered copy of source metadata
        """
        # pylint: disable=protected-access
        filtered_metadata = self._sequence._copy_metadata(deep=True)
        entity_features = settings.get("entity_features", [])

        # Filter entity_descriptors to keep only those in entity_features
        filtered_metadata.entity_descriptors = {
            feat: desc
            for feat, desc in filtered_metadata.entity_descriptors.items()
            if feat in entity_features
        }

        return filtered_metadata

    def _add_duration_to_settings(self, settings, duration_column):
        """
        Add duration column to entity_features in settings.

        Helper for conversions that add a duration feature (e.g., Interval → Event).
        Ensures the duration column is registered in entity_features.

        Args:
            settings (dict): Settings dict with 'entity_features' key
            duration_column (str): Name of duration column to add

        Returns:
            dict: Modified settings with duration_column added
        """
        if duration_column not in settings["entity_features"]:
            settings["entity_features"] = settings["entity_features"] + [
                duration_column
            ]
        return settings

    def _remove_feature_from_settings(self, settings, feature_name):
        """
        Remove a feature from entity_features in settings.

        Helper for conversions that drop features (e.g., Event → Interval with drop_duration).
        Filters out the specified feature from entity_features list.

        Args:
            settings (dict): Settings dict with 'entity_features' key
            feature_name (str): Name of feature to remove

        Returns:
            dict: Modified settings with feature_name removed
        """
        settings["entity_features"] = [
            feat for feat in settings["entity_features"] if feat != feature_name
        ]
        return settings

    def _calculate_duration_column(self, data, temporal_cols):
        """
        Calculate duration from temporal columns (end - start).

        Helper for period sequences (Interval/State) converting to Event.
        Computes duration as the difference between end and start timestamps.
        Works with both datetime (returns timedelta) and numeric timesteps.

        Args:
            data (pd.DataFrame): DataFrame with temporal columns
            temporal_cols (list): List of [start_col, end_col] names

        Returns:
            pd.Series: Duration values (timedelta for datetime, numeric for timesteps)
        """
        return data[temporal_cols[1]] - data[temporal_cols[0]]

    def _rename_temporal_columns(self, data, source_cols, target_names):
        """
        Rename temporal columns in place.

        Args:
            data: DataFrame to modify
            source_cols: List of source column names (1 for events, 2 for periods)
            target_names: Dict with target names. Keys:
                - 'time': For event sequences
                - 'start', 'end': For period sequences (state/interval)

        Returns:
            pd.DataFrame: Modified data (same object, modified in place)

        Examples:
            >>> # Rename event time column
            >>> data = self._rename_temporal_columns(
            ...     data, ['event_time'], {'time': 'timestamp'}
            ... )

            >>> # Rename period columns
            >>> data = self._rename_temporal_columns(
            ...     data, ['start', 'end'], {'start': 'begin', 'end': 'finish'}
            ... )
        """
        col_mapping = {}

        if len(source_cols) == 1:  # Event sequence
            time_col = target_names.get("time")
            if time_col and source_cols[0] != time_col:
                col_mapping[source_cols[0]] = time_col
        else:  # Period sequences (interval/state)
            start_col = target_names.get("start")
            end_col = target_names.get("end")
            if start_col and source_cols[0] != start_col:
                col_mapping[source_cols[0]] = start_col
            if end_col and len(source_cols) > 1 and source_cols[1] != end_col:
                col_mapping[source_cols[1]] = end_col

        if col_mapping:
            data.rename(columns=col_mapping, inplace=True)

        return data
