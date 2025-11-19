#!/usr/bin/env python3
"""
Test automatic metadata inference on SequencePool.
"""

import pytest

from tanat.sequence.base.pool import SequencePool
from tanat.metadata.exception import MetadataInferenceError


class TestSequencePoolInference:
    """Test metadata inference on sequence pools."""

    @pytest.mark.parametrize(
        "seq_type,entity_features",
        [
            ("event", ["event_type"]),
            ("state", ["health_state"]),
            ("interval", ["medication"]),
        ],
    )
    def test_invalid_temporal_raises_inference_error(
        self, invalid_pool_data, seq_type, entity_features
    ):
        """
        Test that invalid temporal data raises MetadataInferenceError.
        Uses invalid_temporal.csv which contains unparseable temporal values.
        """
        df = invalid_pool_data[seq_type]

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
    def test_infer_metadata(self, pool_data, seq_type, entity_features, snapshot):
        """
        Test that metadata is correctly inferred for all sequence types.
        Uses complex_data.csv for each sequence type.
        """
        sequence_data = pool_data[seq_type]

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
            static_data=pool_data["static_data"],
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
    def test_complete_metadata(self, pool_data, seq_type, entity_features, snapshot):
        """
        Test that metadata is correctly completerd.
        """
        sequence_data = pool_data[seq_type]

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
            static_data=pool_data["static_data"],
            metadata={
                "static_descriptors": {
                    "age": {
                        "feature_type": "categorical",  # force age to be categorical
                        "settings": {"categories": ["0-18", "19-35", "36-50", "51+"]},
                    }
                }
            },
        )

        # Snapshot the entire metadata structure
        snapshot.assert_match(pool.metadata)
