#!/usr/bin/env python3
"""
Fixtures for metadata tests.
"""

import pytest
from ..conftest import load_csv


@pytest.fixture(scope="session")
def invalid_pool_data():
    """
    Load invalid temporal datasets for event/state/interval pools.
    Temporal columns contain unparseable data to test validation errors.
    """
    return {
        "event": load_csv("event/invalid_temporal.csv"),
        "state": load_csv("state/invalid_temporal.csv"),
        "interval": load_csv("interval/invalid_temporal.csv"),
    }


@pytest.fixture(scope="session")
def invalid_single_id_data(invalid_pool_data):
    """
    Single-ID versions of invalid temporal datasets.
    """

    def _to_single_id(df):
        if "patient_id" not in df.columns or df.empty:
            return df.copy()
        pid = df["patient_id"].iloc[0]
        return df[df["patient_id"] == pid].reset_index(drop=True)

    return {
        "event": _to_single_id(invalid_pool_data["event"]),
        "state": _to_single_id(invalid_pool_data["state"]),
        "interval": _to_single_id(invalid_pool_data["interval"]),
    }
