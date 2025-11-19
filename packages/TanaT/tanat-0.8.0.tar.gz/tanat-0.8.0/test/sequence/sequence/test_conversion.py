#!/usr/bin/env python3
"""
Test sequence type conversions on individual sequences.
"""

from datetime import datetime, timedelta

import pytest
from pandas.tseries.offsets import DateOffset
import pandas as pd

from tanat.sequence import EventSequence


@pytest.fixture
def event_seq_with_duration_column():
    """
    Individual Event sequence with a duration column properly declared.

    Uses hospital admission/procedure/discharge events with procedure durations.
    """

    # Create event data for a single patient
    event_data = pd.DataFrame(
        {
            "patient_id": [101, 101, 101],
            "timestamp": [
                datetime(2023, 6, 1, 9, 0),
                datetime(2023, 6, 1, 14, 0),
                datetime(2023, 6, 2, 10, 0),
            ],
            "event_type": ["admission", "procedure", "discharge"],
            "location": ["Emergency", "Surgery", "Discharge"],
            "duration_hours": [2.5, 1.5, None],
        }
    )

    # Create sequence with duration feature
    seq = EventSequence(
        id_value=101,
        sequence_data=event_data,
        settings={
            "id_column": "patient_id",
            "time_column": "timestamp",
            "entity_features": ["event_type", "location", "duration_hours"],
        },
    )

    # Declare duration metadata
    seq.update_entity_metadata(
        feature_name="duration_hours", feature_type="duration", granularity="hour"
    )

    return seq


@pytest.fixture
def event_seq_with_timesteps():
    """
    Individual Event sequence with timestep-based temporal data (numeric time).

    Uses simulation-style data with abstract timesteps and numeric durations.
    """
    # Create event data with timesteps for a single sequence
    event_data = pd.DataFrame(
        {
            "patient_id": [101, 101, 101],
            "timestep": [0.0, 5.5, 10.0],
            "event_type": ["start", "medication", "discharge"],
            "severity": ["high", "medium", "low"],
            "duration_units": [5.5, 4.5, None],
        }
    )

    # Create sequence with timestep temporal column
    seq = EventSequence(
        id_value=101,
        sequence_data=event_data,
        settings={
            "id_column": "patient_id",
            "time_column": "timestep",
            "entity_features": ["event_type", "severity", "duration_units"],
        },
    )

    # Declare duration metadata with UNIT granularity
    seq.update_entity_metadata(
        feature_name="duration_units", feature_type="duration", granularity="unit"
    )

    return seq


class TestConversionMethods:
    """
    Tests for sequence type conversion methods on individual sequences.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_as_event_anchor_start(self, sequence_pools, seq_type, snapshot):
        """
        Convert any sequence type to event with anchor='start'.
        """
        seq = sequence_pools[seq_type][3]
        events = seq.as_event(anchor="start")

        snapshot.assert_match(events.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["state", "interval"])
    def test_as_event_anchor_end(self, sequence_pools, seq_type, snapshot):
        """
        Convert State/Interval sequence to Event with anchor='end'.
        """
        seq = sequence_pools[seq_type][3]
        events = seq.as_event(anchor="end")

        snapshot.assert_match(events.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["state", "interval"])
    def test_as_event_anchor_middle(self, sequence_pools, seq_type, snapshot):
        """
        Convert State/Interval sequence to Event with anchor='middle'.
        """
        seq = sequence_pools[seq_type][3]
        events = seq.as_event(anchor="middle")

        snapshot.assert_match(events.sequence_data.to_csv())

    def test_event_to_state_with_end_value(self, sequence_pools, snapshot):
        """
        Convert Event sequence to State with explicit end_value.
        """
        event_seq = sequence_pools["event"][3]
        end_date = datetime(2024, 1, 15, 0, 0)

        state_seq = event_seq.as_state(end_value=end_date)

        snapshot.assert_match(state_seq.sequence_data.to_csv())

    def test_event_to_state_custom_columns(self, sequence_pools, snapshot):
        """
        Convert Event sequence to State with custom column names.
        """
        event_seq = sequence_pools["event"][3]
        end_date = datetime(2024, 1, 15, 0, 0)

        state_seq = event_seq.as_state(
            end_value=end_date, start_column="begin", end_column="finish"
        )

        snapshot.assert_match(state_seq.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["state", "interval"])
    def test_as_interval_identity(self, sequence_pools, seq_type, snapshot):
        """
        Convert State/Interval sequence to Interval (trivial/identity).
        """
        seq = sequence_pools[seq_type][3]
        intervals = seq.as_interval()

        snapshot.assert_match(intervals.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["state", "interval"])
    def test_as_interval_custom_columns(self, sequence_pools, seq_type, snapshot):
        """
        Convert State/Interval sequence to Interval with custom column names.
        """
        seq = sequence_pools[seq_type][3]
        intervals = seq.as_interval(start_column="begin", end_column="finish")

        snapshot.assert_match(intervals.sequence_data.to_csv())

    @pytest.mark.parametrize("duration", [timedelta(hours=6), DateOffset(days=1)])
    def test_event_to_interval_fixed_duration(self, sequence_pools, duration, snapshot):
        """
        Convert Event sequence to Interval with various fixed durations.
        """
        event_seq = sequence_pools["event"][3]
        interval_seq = event_seq.as_interval(duration=duration)

        snapshot.assert_match(interval_seq.sequence_data.to_csv())

    def test_event_to_interval_duration_column(
        self, event_seq_with_duration_column, snapshot
    ):
        """
        Convert Event sequence to Interval using a duration column.
        """
        event_seq = event_seq_with_duration_column
        interval_seq = event_seq.as_interval(duration="duration_hours")

        snapshot.assert_match(interval_seq.sequence_data.to_csv())

    def test_event_to_interval_numeric_duration_with_timesteps(
        self, event_seq_with_timesteps, snapshot
    ):
        """
        Convert Event sequence to Interval with numeric duration (timestep-based).

        Uses UNIT granularity where both time and duration are numeric (floats).
        """
        event_seq = event_seq_with_timesteps

        # Convert using numeric duration (scalar)
        interval_scalar = event_seq.as_interval(duration=2.5)
        snapshot.assert_match(interval_scalar.sequence_data.to_csv())

        # Convert using duration column
        interval_column = event_seq.as_interval(duration="duration_units")
        snapshot.assert_match(interval_column.sequence_data.to_csv())

    def test_event_to_interval_without_duration_raises(self, sequence_pools):
        """
        Converting Event to Interval without duration raises NotImplementedError.
        """
        event_seq = sequence_pools["event"][3]

        with pytest.raises(NotImplementedError):
            event_seq.as_interval()

    def test_event_to_interval_invalid_duration_column_raises(self, sequence_pools):
        """
        Using a non-existent duration column raises ValueError.
        """
        event_seq = sequence_pools["event"][3]

        with pytest.raises(ValueError, match="must be declared as an entity feature"):
            event_seq.as_interval(duration="nonexistent_column")

    def test_single_event_to_state(self, sequence_pools, snapshot):
        """
        Convert single-event sequence to State.
        """
        event_seq = sequence_pools["event"][3]
        state_seq = event_seq.as_state(end_value=datetime(2024, 1, 15, 0, 0))
        snapshot.assert_match(state_seq.sequence_data.to_csv())

    def test_single_event_to_interval(self, sequence_pools, snapshot):
        """
        Convert single-event sequence to Interval.
        """
        event_seq = sequence_pools["event"][3]
        interval_seq = event_seq.as_interval(duration=timedelta(hours=6))
        snapshot.assert_match(interval_seq.sequence_data.to_csv())

    def test_event_to_interval_with_drop_duration_feature(
        self, event_seq_with_duration_column, snapshot
    ):
        """
        Convert Event sequence to Interval with drop_duration_feature=True.
        """
        event_seq = event_seq_with_duration_column

        # Convert WITH dropping duration
        interval_drop = event_seq.as_interval(
            duration="duration_hours", drop_duration_feature=True
        )

        snapshot.assert_match(interval_drop.sequence_data.to_csv())
        snapshot.assert_match(interval_drop.metadata)

    def test_event_to_interval_with_drop_duration_timesteps(
        self, event_seq_with_timesteps, snapshot
    ):
        """
        Convert Event sequence (timestep) to Interval with drop_duration_feature=True.
        """
        event_seq = event_seq_with_timesteps

        # Convert WITH dropping duration
        interval_drop = event_seq.as_interval(
            duration="duration_units", drop_duration_feature=True
        )

        # Snapshot
        snapshot.assert_match(interval_drop.sequence_data.to_csv())
        snapshot.assert_match(interval_drop.metadata)

    @pytest.mark.parametrize("seq_type", ["interval", "state"])
    def test_interval_state_to_event_with_add_duration(
        self, sequence_pools, seq_type, snapshot
    ):
        """
        Convert Interval/State sequence to Event with add_duration_feature=True.
        """
        seq = sequence_pools[seq_type][3]
        # Convert WITH adding duration
        event_with_duration = seq.as_event(
            anchor="start", add_duration_feature=True, duration_column="duration"
        )

        snapshot.assert_match(event_with_duration.sequence_data.to_csv())
        snapshot.assert_match(event_with_duration.metadata)


class TestConversionChaining:
    """
    Tests for chaining multiple conversions on individual sequences.
    """

    def test_event_to_state_to_event_roundtrip(self, sequence_pools, snapshot):
        """
        Roundtrip: Event -> State -> Event on individual sequence.
        """
        event_seq = sequence_pools["event"][3]

        state_seq = event_seq.as_state(end_value=datetime(2024, 1, 15, 0, 0))
        event_back = state_seq.as_event(anchor="start")

        snapshot.assert_match(event_back.sequence_data.to_csv())

    def test_event_to_interval_to_event_roundtrip(self, sequence_pools, snapshot):
        """
        Roundtrip: Event -> Interval -> Event on individual sequence.
        """
        event_seq = sequence_pools["event"][3]

        interval_seq = event_seq.as_interval(duration=timedelta(hours=6))
        event_back = interval_seq.as_event(anchor="start")

        snapshot.assert_match(event_back.sequence_data.to_csv())

    def test_state_to_interval_to_event_chain(self, sequence_pools, snapshot):
        """
        Chain: State -> Interval -> Event on individual sequence.
        """
        state_seq = sequence_pools["state"][3]

        interval_seq = state_seq.as_interval()
        event_seq = interval_seq.as_event(anchor="middle")

        snapshot.assert_match(event_seq.sequence_data.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_multiple_conversions_preserve_data(self, sequence_pools, seq_type):
        """
        Multiple conversions should preserve data integrity.
        """
        seq = sequence_pools[seq_type][3]
        original_len = len(seq.sequence_data)

        # Perform conversion chain
        if seq_type == "event":
            result = (
                seq.as_state(end_value=datetime(2024, 1, 15, 0, 0))
                .as_interval()
                .as_event(anchor="start")
            )
        elif seq_type == "state":
            result = seq.as_interval().as_event(anchor="start")
        else:
            result = seq.as_event(anchor="start")

        assert len(result.sequence_data) == original_len


class TestMetadataPreservation:
    """
    Tests that metadata is preserved during conversions on individual sequences.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_entity_metadata_preserved(self, sequence_pools, seq_type, snapshot):
        """
        Entity metadata should be preserved during conversion on individual sequence.
        """
        seq = sequence_pools[seq_type][3].copy()

        # Get an entity feature and update its metadata
        entity_feature = seq.settings.entity_features[0]
        seq.update_entity_metadata(
            feature_name=entity_feature, feature_type="categorical"
        )

        # Convert to another type
        if seq_type == "event":
            converted = seq.as_state(end_value=datetime(2024, 1, 15, 0, 0))
        else:
            converted = seq.as_event(anchor="start")

        # Check metadata preserved
        snapshot.assert_match(converted.metadata)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_temporal_metadata_preserved(self, sequence_pools, seq_type, snapshot):
        """
        Temporal metadata should be preserved during conversions.
        """
        seq = sequence_pools[seq_type][3].copy()

        # Update temporal metadata
        seq.update_temporal_metadata(timezone="Europe/Paris")

        # Convert to another type
        if seq_type == "event":
            converted = seq.as_interval(duration=timedelta(hours=6))
        elif seq_type == "state":
            converted = seq.as_interval()
        else:
            converted = seq.as_event(anchor="start")

        # Check temporal metadata preserved
        snapshot.assert_match(converted.metadata)
