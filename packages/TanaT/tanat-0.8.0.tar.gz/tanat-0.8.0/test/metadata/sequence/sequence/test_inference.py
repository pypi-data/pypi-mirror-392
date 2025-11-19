#!/usr/bin/env python3
"""
Test automatic metadata inference on single sequences.
"""

import pytest

from tanat.sequence.base.pool import SequencePool
from tanat.metadata.exception import MetadataInferenceError


class TestSingleSequenceInference:
    """Test metadata inference on individual sequences (single ID)."""

    @pytest.mark.parametrize(
        "seq_type,entity_features",
        [
            ("event", ["event_type"]),
            ("state", ["health_state"]),
            ("interval", ["medication"]),
        ],
    )
    def test_invalid_temporal_raises_inference_error(
        self, invalid_single_id_data, seq_type, entity_features
    ):
        """
        Test that invalid temporal data raises MetadataInferenceError.
        Single sequence version: one patient with unparseable temporal values.
        """
        df = invalid_single_id_data[seq_type]

        settings = {"id_column": "patient_id"}
        if seq_type == "event":
            settings["time_column"] = "date"
        else:
            settings["start_column"] = "start_date"
            settings["end_column"] = "end_date"
        settings["entity_features"] = entity_features

        with pytest.raises(MetadataInferenceError):
            _ = SequencePool.init(
                seq_type, df, settings, metadata=None, static_data=None
            )

    @pytest.mark.parametrize(
        "seq_type,entity_features",
        [
            ("event", ["event_type", "provider"]),
            ("state", ["health_state", "condition"]),
            ("interval", ["medication", "administration_route", "dosage"]),
        ],
    )
    def test_infer_metadata(self, single_id_data, seq_type, entity_features, snapshot):
        """
        Test that metadata is correctly inferred for single sequences.
        Single sequence version: one patient with valid temporal data.
        """
        sequence_data = single_id_data[seq_type]

        settings = {"id_column": "patient_id"}
        if seq_type == "event":
            settings["time_column"] = "date"
        else:
            settings["start_column"] = "start_date"
            settings["end_column"] = "end_date"
        settings["entity_features"] = entity_features
        settings["static_features"] = [
            "gender",
            "age",
            "insurance",
            "chronic_condition",
        ]

        pool = SequencePool.init(
            seq_type,
            sequence_data,
            settings=settings,
            static_data=single_id_data["static_data"],
        )

        # Snapshot the entire metadata structure
        snapshot.assert_match(pool.metadata)

    @pytest.mark.parametrize(
        "seq_type,entity_features",
        [
            ("event", ["event_type", "provider"]),
            ("state", ["health_state", "condition"]),
            ("interval", ["medication", "administration_route", "dosage"]),
        ],
    )
    def test_complete_metadata(
        self, single_id_data, seq_type, entity_features, snapshot
    ):
        """
        Test that metadata is correctly completed with partial override.
        Single sequence version: force age to categorical.
        """
        sequence_data = single_id_data[seq_type]

        settings = {"id_column": "patient_id"}
        if seq_type == "event":
            settings["time_column"] = "date"
        else:
            settings["start_column"] = "start_date"
            settings["end_column"] = "end_date"
        settings["entity_features"] = entity_features
        settings["static_features"] = [
            "gender",
            "age",
            "insurance",
            "chronic_condition",
        ]

        pool = SequencePool.init(
            seq_type,
            sequence_data,
            settings=settings,
            static_data=single_id_data["static_data"],
            metadata={
                "static_descriptors": {
                    "age": {
                        "feature_type": "categorical",
                        "settings": {"categories": ["0-18", "19-35", "36-50", "51+"]},
                    }
                }
            },
        )

        # Snapshot the entire metadata structure
        snapshot.assert_match(pool.metadata)
