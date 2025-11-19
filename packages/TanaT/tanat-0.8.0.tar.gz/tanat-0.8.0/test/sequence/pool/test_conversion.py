#!/usr/bin/env python3
"""
Test sequence type conversions on sequence pools.
"""

from datetime import datetime, timedelta

import pytest
from pandas.tseries.offsets import DateOffset
import pandas as pd

from tanat.sequence import EventSequencePool


@pytest.fixture
def event_pool_with_duration_column():
    """
    Event pool with a duration column properly declared.

    Uses hospital admission/procedure/discharge events with procedure durations.
    """
    # Create event data similar to conversion.ipynb
    event_data = pd.DataFrame(
        {
            "patient_id": [101, 101, 101, 102, 102, 103, 103],
            "timestamp": [
                datetime(2023, 6, 1, 9, 0),
                datetime(2023, 6, 1, 14, 0),
                datetime(2023, 6, 2, 10, 0),
                datetime(2023, 6, 1, 10, 30),
                datetime(2023, 6, 1, 18, 0),
                datetime(2023, 6, 1, 11, 0),
                datetime(2023, 6, 1, 15, 30),
            ],
            "event_type": [
                "admission",
                "procedure",
                "discharge",
                "admission",
                "procedure",
                "admission",
                "procedure",
            ],
            "location": [
                "Emergency",
                "Surgery",
                "Discharge",
                "Emergency",
                "Radiology",
                "Emergency",
                "Surgery",
            ],
            "duration_hours": [2.5, 1.5, None, 3.0, 1.0, 2.0, 2.5],
        }
    )

    # Create pool with duration feature
    pool = EventSequencePool(
        sequence_data=event_data,
        settings={
            "id_column": "patient_id",
            "time_column": "timestamp",
            "entity_features": ["event_type", "location", "duration_hours"],
        },
    )

    # Declare duration metadata
    pool.update_entity_metadata(
        feature_name="duration_hours", feature_type="duration", granularity="hour"
    )

    return pool


@pytest.fixture
def event_pool_with_timesteps():
    """
    Event pool with timestep-based temporal data (numeric time).

    Uses simulation-style data with abstract timesteps and numeric durations.
    """
    # Create event data with timesteps (floats) instead of datetimes
    event_data = pd.DataFrame(
        {
            "patient_id": [101, 101, 101, 102, 102, 103],
            "timestep": [0.0, 5.5, 10.0, 0.0, 3.25, 2.0],
            "event_type": [
                "start",
                "medication",
                "discharge",
                "start",
                "test",
                "procedure",
            ],
            "severity": ["high", "medium", "low", "medium", "low", "high"],
            "duration_units": [5.5, 4.5, None, 3.25, 1.75, 2.0],
        }
    )

    # Create pool with timestep temporal column
    pool = EventSequencePool(
        sequence_data=event_data,
        settings={
            "id_column": "patient_id",
            "time_column": "timestep",
            "entity_features": ["event_type", "severity", "duration_units"],
        },
    )

    # Declare duration metadata with UNIT granularity
    pool.update_entity_metadata(
        feature_name="duration_units", feature_type="duration", granularity="unit"
    )

    return pool


class TestConversionMethods:
    """
    Tests for sequence type conversion methods on pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_as_event_anchor_start(self, sequence_pools, pool_type, snapshot):
        """
        Convert any pool type to event with anchor='start'.
        """
        pool = sequence_pools[pool_type]
        events = pool.as_event(anchor="start")

        snapshot.assert_match(events.sequence_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["state", "interval"])
    def test_as_event_anchor_end(self, sequence_pools, pool_type, snapshot):
        """
        Convert State/Interval to Event with anchor='end'.
        """
        pool = sequence_pools[pool_type]
        events = pool.as_event(anchor="end")

        snapshot.assert_match(events.sequence_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["state", "interval"])
    def test_as_event_anchor_middle(self, sequence_pools, pool_type, snapshot):
        """
        Convert State/Interval to Event with anchor='middle'.
        """
        pool = sequence_pools[pool_type]
        events = pool.as_event(anchor="middle")

        snapshot.assert_match(events.sequence_data.to_csv())

    def test_event_to_state_with_end_value(self, sequence_pools, snapshot):
        """
        Convert Event to State with explicit end_value.
        """
        events = sequence_pools["event"]
        end_date = datetime(2024, 1, 15, 0, 0)

        states = events.as_state(end_value=end_date)

        snapshot.assert_match(states.sequence_data.to_csv())

    def test_event_to_state_custom_columns(self, sequence_pools, snapshot):
        """
        Convert Event to State with custom column names.
        """
        events = sequence_pools["event"]
        end_date = datetime(2024, 1, 15, 0, 0)

        states = events.as_state(
            end_value=end_date, start_column="begin", end_column="finish"
        )

        snapshot.assert_match(states.sequence_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["state", "interval"])
    def test_as_interval_identity(self, sequence_pools, pool_type, snapshot):
        """
        Convert State/Interval to Interval (trivial/identity conversion).
        """
        pool = sequence_pools[pool_type]
        intervals = pool.as_interval()

        snapshot.assert_match(intervals.sequence_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["state", "interval"])
    def test_as_interval_custom_columns(self, sequence_pools, pool_type, snapshot):
        """
        Convert State/Interval to Interval with custom column names.
        """
        pool = sequence_pools[pool_type]
        intervals = pool.as_interval(start_column="begin", end_column="finish")

        snapshot.assert_match(intervals.sequence_data.to_csv())

    @pytest.mark.parametrize("duration", [timedelta(hours=6), DateOffset(days=1)])
    def test_event_to_interval_fixed_duration(self, sequence_pools, duration, snapshot):
        """
        Convert Event to Interval with various fixed duration types.
        """
        events = sequence_pools["event"]
        intervals = events.as_interval(duration=duration)

        snapshot.assert_match(intervals.sequence_data.to_csv())

    def test_event_to_interval_duration_column(
        self, event_pool_with_duration_column, snapshot
    ):
        """
        Convert Event to Interval using a duration column.
        """
        events = event_pool_with_duration_column
        intervals = events.as_interval(duration="duration_hours")

        snapshot.assert_match(intervals.sequence_data.to_csv())

    def test_event_to_interval_numeric_duration_with_timesteps(
        self, event_pool_with_timesteps, snapshot
    ):
        """
        Convert Event to Interval with numeric duration (timestep-based sequences).

        Uses UNIT granularity where both time and duration are numeric (floats).
        """
        events = event_pool_with_timesteps

        # Convert using numeric duration (scalar)
        intervals_scalar = events.as_interval(duration=2.5)
        snapshot.assert_match(intervals_scalar.sequence_data.to_csv())

        # Convert using duration column
        intervals_column = events.as_interval(duration="duration_units")
        snapshot.assert_match(intervals_column.sequence_data.to_csv())

    def test_event_to_interval_without_duration_raises(self, sequence_pools):
        """
        Converting Event to Interval without duration parameter raises NotImplementedError.
        """
        events = sequence_pools["event"]

        with pytest.raises(NotImplementedError):
            events.as_interval()

    def test_event_to_interval_invalid_duration_column_raises(self, sequence_pools):
        """
        Using a non-existent duration column raises ValueError.
        """
        events = sequence_pools["event"]

        with pytest.raises(ValueError):
            events.as_interval(duration="nonexistent_column")

    def test_event_to_interval_undeclared_duration_raises(
        self, event_pool_with_duration_column
    ):
        """
        Using a column without duration metadata raises ValueError.
        """

        copy_event_pool = event_pool_with_duration_column.copy()

        # Update metadata to remove duration feature type
        copy_event_pool.update_entity_metadata(
            feature_name="duration_hours", feature_type="numerical"
        )

        with pytest.raises(ValueError):
            copy_event_pool.as_interval(duration="duration_hours")

    def test_event_to_interval_with_drop_duration_feature(
        self, event_pool_with_duration_column, snapshot
    ):
        """
        Convert Event to Interval with drop_duration_feature=True.
        """
        events = event_pool_with_duration_column.copy()

        # Convert WITH dropping duration
        intervals_drop = events.as_interval(
            duration="duration_hours", drop_duration_feature=True
        )

        # Snapshot data and metadata
        snapshot.assert_match(intervals_drop.sequence_data.to_csv())
        snapshot.assert_match(intervals_drop.metadata)

    def test_event_to_interval_with_drop_duration_timesteps(
        self, event_pool_with_timesteps, snapshot
    ):
        """
        Convert Event (timestep) to Interval with drop_duration_feature=True.
        """
        events = event_pool_with_timesteps.copy()

        # Convert WITH dropping duration
        intervals_drop = events.as_interval(
            duration="duration_units", drop_duration_feature=True
        )

        # Snapshot
        snapshot.assert_match(intervals_drop.sequence_data.to_csv())
        snapshot.assert_match(intervals_drop.metadata)

    @pytest.mark.parametrize("pool_type", ["interval", "state"])
    def test_interval_state_to_event_with_add_duration(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Convert Interval/State to Event with add_duration_feature=True.
        """
        pool = sequence_pools[pool_type].copy()
        # Convert WITH adding duration
        events_with_duration = pool.as_event(
            anchor="start", add_duration_feature=True, duration_column="duration"
        )

        snapshot.assert_match(events_with_duration.sequence_data.to_csv())
        snapshot.assert_match(events_with_duration.metadata)


class TestConversionChaining:
    """
    Tests for chaining multiple conversions (roundtrips).
    """

    def test_event_to_state_to_event_roundtrip(self, sequence_pools, snapshot):
        """
        Roundtrip: Event -> State -> Event.
        """
        events = sequence_pools["event"]

        states = events.as_state(end_value=datetime(2024, 1, 15, 0, 0))
        events_back = states.as_event(anchor="start")

        snapshot.assert_match(events_back.sequence_data.to_csv())

    def test_event_to_interval_to_event_roundtrip(self, sequence_pools, snapshot):
        """
        Roundtrip: Event -> Interval -> Event.
        """
        events = sequence_pools["event"]

        intervals = events.as_interval(duration=timedelta(hours=6))
        events_back = intervals.as_event(anchor="start")

        snapshot.assert_match(events_back.sequence_data.to_csv())

    def test_state_to_interval_to_event_chain(self, sequence_pools, snapshot):
        """
        Chain: State -> Interval -> Event.
        """
        states = sequence_pools["state"]

        intervals = states.as_interval()
        events = intervals.as_event(anchor="middle")

        snapshot.assert_match(events.sequence_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_multiple_conversions_preserve_length(self, sequence_pools, pool_type):
        """
        Multiple conversions should preserve sequence lengths.
        """
        pool = sequence_pools[pool_type]
        original_len = len(pool.sequence_data)

        # Chain of conversions
        if pool_type == "event":
            result = (
                pool.as_state(end_value=datetime(2024, 1, 15, 0, 0))
                .as_interval()
                .as_event(anchor="start")
            )
        elif pool_type == "state":
            result = (
                pool.as_interval()
                .as_event(anchor="start")
                .as_state(end_value=datetime(2024, 1, 15, 0, 0))
            )
        else:  # interval
            result = (
                pool.as_event(anchor="start")
                .as_state(end_value=datetime(2024, 1, 15, 0, 0))
                .as_interval()
            )

        assert len(result.sequence_data) == original_len


class TestMetadataPreservation:
    """
    Tests that metadata is properly preserved during conversions.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_entity_metadata_preserved(self, sequence_pools, pool_type, snapshot):
        """
        Entity feature metadata should be preserved during conversions.
        """
        pool = sequence_pools[pool_type].copy()

        # Get an entity feature and update its metadata
        entity_feature = pool.settings.entity_features[0]
        pool.update_entity_metadata(
            feature_name=entity_feature, feature_type="categorical"
        )

        # Convert to another type
        if pool_type == "event":
            converted = pool.as_state(end_value=datetime(2024, 1, 15, 0, 0))
        else:
            converted = pool.as_event(anchor="start")

        # Check metadata preserved
        snapshot.assert_match(converted.metadata)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_temporal_metadata_preserved(self, sequence_pools, pool_type, snapshot):
        """
        Temporal metadata should be preserved during conversions.
        """
        pool = sequence_pools[pool_type].copy()

        # Update temporal metadata
        pool.update_temporal_metadata(timezone="Europe/Paris")

        # Convert to another type
        if pool_type == "event":
            converted = pool.as_interval(duration=timedelta(hours=6))
        elif pool_type == "state":
            converted = pool.as_interval()
        else:
            converted = pool.as_event(anchor="start")

        # Check temporal metadata preserved
        snapshot.assert_match(converted.metadata)
