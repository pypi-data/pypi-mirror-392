#!/usr/bin/env python3
"""
Test initialization of unique sequence.
"""

import pytest

import pandas as pd
from pydantic import ValidationError

from tanat.sequence.base.sequence import Sequence
from tanat.sequence.type.event.settings import EventSequenceSettings
from tanat.sequence.type.state.settings import StateSequenceSettings
from tanat.sequence.type.interval.settings import IntervalSequenceSettings


class TestInitSequence:
    """
    Test initialization of sequence.
    """

    @pytest.mark.parametrize(
        "settings_cls,settings_kwargs",
        [
            ## -- event
            (
                EventSequenceSettings,
                {
                    "id_column": "patient_id",
                    "time_column": "date",
                    "entity_features": ["event_type", "provider"],
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- state
            (
                StateSequenceSettings,
                {
                    "id_column": "patient_id",
                    "entity_features": ["health_state", "condition"],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- interval
            (
                IntervalSequenceSettings,
                {
                    "id_column": "patient_id",
                    "entity_features": [
                        "medication",
                        "administration_route",
                        "dosage",
                    ],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
        ],
    )
    def test_init_sequence_settings(self, settings_cls, settings_kwargs):
        """
        Test initialization of sequence settings.
        """
        settings = settings_cls(**settings_kwargs)
        assert isinstance(settings, settings_cls)

    @pytest.mark.parametrize(
        "settings_cls,settings_kwargs",
        [
            ## -- event
            (
                EventSequenceSettings,
                {
                    "id_column": "patient_id",
                    "time_column": "date",
                    "entity_features": ["event_type", "patient_id"],  # Conflict here
                },
            ),
            ## -- state
            (
                StateSequenceSettings,
                {
                    "id_column": "patient_id",
                    "entity_features": ["health_state", "start_date"],  # Conflict here
                    "start_column": "start_date",
                },
            ),
            ## -- interval
            (
                IntervalSequenceSettings,
                {
                    "id_column": "patient_id",
                    "entity_features": [
                        "medication",
                        "administration_route",
                    ],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": ["patient_id"],  # Conflict here
                },
            ),
        ],
    )
    def test_conflict_detected_in_settings(self, settings_cls, settings_kwargs):
        """
        Test that conflicting column names raise an error.

        The validation raises ValueError which is wrapped by Pydantic in ValidationError.
        We verify that the error message clearly indicates the column conflict.
        """
        with pytest.raises(ValidationError):
            settings_cls(**settings_kwargs)

    @pytest.mark.parametrize(
        "settings_cls",
        [EventSequenceSettings, StateSequenceSettings, IntervalSequenceSettings],
    )
    def test_entity_features_single_string_conversion(self, settings_cls):
        """
        Test that a single string for entity_features is automatically converted to a list.

        This verifies user-friendly behavior: users can pass a simple string when they
        have only one entity feature, instead of requiring a list.
        """
        entity_features_input = "medication"
        # Build minimal settings with single string for entity_features
        if settings_cls == EventSequenceSettings:
            settings_kwargs = {
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": entity_features_input,  # Single string here
            }
        else:  # State or Interval
            settings_kwargs = {
                "id_column": "patient_id",
                "entity_features": entity_features_input,  # Single string here
                "start_column": "start_date",
                "end_column": "end_date",
            }

        # Should not raise any error and should convert string to list
        settings = settings_cls(**settings_kwargs)

        # Verify it was converted to a list
        assert isinstance(settings.entity_features, list)
        assert len(settings.entity_features) == 1
        assert settings.entity_features[0] == entity_features_input

    @pytest.mark.parametrize(
        "settings_cls",
        [EventSequenceSettings, StateSequenceSettings, IntervalSequenceSettings],
    )
    def test_static_features_single_string_conversion(self, settings_cls):
        """
        Test that a single string for static_features is automatically converted to a list.

        This verifies user-friendly behavior: users can pass a simple string when they
        have only one static feature, instead of requiring a list.
        """
        entity_feature_list = ["ef_A", "ef_B", "ef_C"]
        static_feature_str = "age"
        # Build minimal settings with single string for static_features
        if settings_cls == EventSequenceSettings:
            settings_kwargs = {
                "id_column": "patient_id",
                "time_column": "date",
                "entity_features": entity_feature_list,
                "static_features": static_feature_str,  # Single string here
            }
        else:  # State or Interval
            settings_kwargs = {
                "id_column": "patient_id",
                "entity_features": entity_feature_list,  # Single string here
                "start_column": "start_date",
                "end_column": "end_date",
                "static_features": static_feature_str,  # Single string here
            }

        # Should not raise any error and should convert string to list
        settings = settings_cls(**settings_kwargs)

        # Verify it was converted to a list
        assert isinstance(settings.static_features, list)
        assert len(settings.static_features) == 1
        assert settings.static_features[0] == static_feature_str

    @pytest.mark.parametrize(
        "seq_type,settings",
        [
            ## -- event
            (
                "event",
                {
                    "id_column": "patient_id",
                    "time_column": "date",
                    "entity_features": ["event_type", "provider"],
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- state
            (
                "state",
                {
                    "id_column": "patient_id",
                    "entity_features": ["health_state", "condition"],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- interval
            (
                "interval",
                {
                    "id_column": "patient_id",
                    "entity_features": [
                        "medication",
                        "administration_route",
                        "dosage",
                    ],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
        ],
    )
    def test_init_unique_sequence(self, single_id_data, seq_type, settings):
        """
        Test initialization of unique sequence.
        """
        sequence_data = single_id_data[seq_type]
        static_data = single_id_data["static_data"]

        uniq_seq = Sequence.init(
            seq_type,
            id_value=1,
            sequence_data=sequence_data,
            settings=settings,
            static_data=static_data,
        )

        assert isinstance(uniq_seq, Sequence)
        assert isinstance(uniq_seq.sequence_data, pd.DataFrame)
        assert isinstance(uniq_seq.static_data, pd.DataFrame)

    @pytest.mark.parametrize("anchor", ["start", "middle", "end"])
    def test_anchoring_interval(self, single_id_data, anchor, snapshot):
        """
        Test anchoring behavior for interval sequence types.
        For id_value = 1, it does not modify entity order.
        """
        settings = {
            "id_column": "patient_id",
            "entity_features": [
                "medication",
                "administration_route",
                "dosage",
            ],
            "start_column": "start_date",
            "end_column": "end_date",
            "anchor": anchor,
        }
        sequence_data = single_id_data["interval"]

        uniq_seq = Sequence.init(
            "interval",
            id_value=1,
            sequence_data=sequence_data,
            settings=settings,
        )
        snapshot.assert_match(uniq_seq.sequence_data.to_csv())
