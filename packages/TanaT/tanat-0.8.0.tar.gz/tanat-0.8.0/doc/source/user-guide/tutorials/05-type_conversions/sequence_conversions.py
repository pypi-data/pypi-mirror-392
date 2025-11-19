# %% [markdown]
# .. _type_conversions_tutorial:
#
# # Sequence Type Conversions
#
# This tutorial demonstrates conversions between the three temporal sequence types:
# - **Event**: point-in-time occurrences
# - **State**: continuous periods with status values
# - **Interval**: time periods with durations
#
# We'll use a simple hospital patient journey to illustrate each conversion.

# %% [markdown]
# ## Setup

# %%
from datetime import datetime, timedelta
import pandas as pd
from tanat.sequence import EventSequencePool

# %% [markdown]
# ## Sample Data: Hospital Patient Journeys
#
# Three patients with different admission/transfer/discharge events.

# %%
# Event data: admission, transfers, and discharge events
event_data = pd.DataFrame(
    {
        "patient_id": [101, 101, 101, 101, 102, 102, 102, 103, 103, 103],
        "timestamp": [
            datetime(2023, 6, 1, 9, 0),  # Patient 101
            datetime(2023, 6, 1, 14, 0),
            datetime(2023, 6, 2, 10, 0),
            datetime(2023, 6, 2, 16, 0),
            datetime(2023, 6, 1, 10, 30),  # Patient 102
            datetime(2023, 6, 1, 18, 0),
            datetime(2023, 6, 2, 12, 0),
            datetime(2023, 6, 1, 11, 0),  # Patient 103
            datetime(2023, 6, 1, 15, 30),
            datetime(2023, 6, 2, 14, 0),
        ],
        "event_type": [
            "admission",
            "transfer",
            "transfer",
            "discharge",
            "admission",
            "transfer",
            "discharge",
            "admission",
            "transfer",
            "discharge",
        ],
        "location": [
            "Emergency",
            "ICU",
            "Ward",
            None,
            "Emergency",
            "Ward",
            None,
            "Emergency",
            "ICU",
            None,
        ],
    }
)

events_pool = EventSequencePool(
    sequence_data=event_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["event_type", "location"],
    },
)

print("EventSequencePool created")
events_pool

# %% [markdown]
# ## 1. Event to State Conversion
#
# Convert events to continuous states by specifying:
# - `state_value_col`: the column containing state values
# - `end_value`: a datetime to use as the end time for the last state in each sequence
#
# The `end_value` parameter sets when all final states terminate (e.g., current date).

# %%
# Convert events to states
# All sequences will end on June 3, 2023
states_pool = events_pool.as_state(end_value=datetime(2023, 6, 3, 0, 0))

states_pool

# %% [markdown]
# ## 2. State to Event Conversion
#
# Extract events from states using the `anchor` parameter:
# - `"start"`: event at the beginning of each state
# - `"end"`: event at the end of each state
# - `"both"`: events at both start and end

# %%
# Extract start events => back to original events pool
events_from_start = states_pool.as_event(anchor="start")
events_from_start

# %%
# Extract end events
events_from_end = states_pool.as_event(anchor="end")
events_from_end

# %% [markdown]
# ## 3. State to Interval Conversion
#
# State and Interval are structurally equivalent (both have start/end times). The conversion is trivial.

# %%
# Convert states to intervals
intervals_pool = states_pool.as_interval()
intervals_pool

# %% [markdown]
# ## 4. Event to Interval with Duration
#
# Convert events to intervals by specifying a duration. Duration can be:
# - A scalar `timedelta` (fixed duration for all events)
# - A column name containing duration values
# - A `DateOffset` for calendar-aware durations

# %% [markdown]
# ### 4.1 Fixed Duration (timedelta)

# %%
# Medication events with fixed 6-hour duration
medication_data = pd.DataFrame(
    {
        "patient_id": [101, 101, 102, 103],
        "timestamp": [
            datetime(2023, 6, 1, 10, 0),
            datetime(2023, 6, 1, 16, 0),
            datetime(2023, 6, 1, 12, 0),
            datetime(2023, 6, 1, 14, 0),
        ],
        "medication": ["Antibiotics", "Painkillers", "Antibiotics", "Antibiotics"],
    }
)

medications_pool = EventSequencePool(
    sequence_data=medication_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["medication"],
    },
)

# Convert with fixed duration
medication_intervals = medications_pool.as_interval(duration=timedelta(hours=6))
medication_intervals

# %% [markdown]
# ### 4.2 Variable Duration (column)
#
# When each event has its own duration, we recommend storing the duration in a column and declare it as a duration feature.

# %%
# Procedure events with variable durations
procedure_data = pd.DataFrame(
    {
        "patient_id": [101, 102, 103],
        "timestamp": [
            datetime(2023, 6, 1, 11, 0),
            datetime(2023, 6, 1, 13, 0),
            datetime(2023, 6, 1, 16, 0),
        ],
        "procedure": ["X-Ray", "X-Ray", "MRI"],
        "duration_hours": [1, 1, 2],  # Variable durations
    }
)

procedures_pool = EventSequencePool(
    sequence_data=procedure_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["procedure", "duration_hours"],
    },
)

# Declare the duration column
procedures_pool.update_entity_metadata(
    feature_name="duration_hours", feature_type="duration", granularity="hour"
)

# Convert using the duration column
procedure_intervals = procedures_pool.as_interval(duration="duration_hours")
procedure_intervals

# %% [markdown]
# ### 4.3 Calendar-Aware Duration (DateOffset)
#
# For durations in months or years, we use `DateOffset` which handles variable month lengths correctly.

# %%
# Treatment events with calendar-aware durations
treatment_data = pd.DataFrame(
    {
        "patient_id": [101, 102, 103],
        "start_date": [
            datetime(2023, 1, 15),
            datetime(2023, 2, 28),
            datetime(2020, 2, 29),  # Leap year
        ],
        "treatment": ["Chemotherapy", "Radiotherapy", "Chemotherapy"],
        "duration_months": [3, 2, 6],  # Durations in months
    }
)

treatments_pool = EventSequencePool(
    sequence_data=treatment_data,
    settings={
        "id_column": "patient_id",
        "time_column": "start_date",
        "entity_features": ["treatment", "duration_months"],
    },
)

# Declare duration with calendar granularity
treatments_pool.update_entity_metadata(
    feature_name="duration_months",
    feature_type="duration",
    granularity="month",
)

# Convert with calendar-aware durations
treatment_intervals = treatments_pool.as_interval(duration="duration_months")
treatment_intervals

# %% [markdown]
# ### 4.4 Timestep-Based Sequences with UNIT Granularity
#
# When working with data when time is encoded as `timestep`, use the `UNIT` granularity for durations. This preserves timesteps as floats without converting to timedelta.

# %%
# Simulation data with abstract timesteps and fractional durations
timestep_data = pd.DataFrame(
    {
        "patient_id": [101, 101, 101, 102, 102, 103],
        "timestep": [0.0, 5.0, 10.0, 0.0, 3.0, 2.0],
        "event_type": [
            "start",
            "medication",
            "discharge",
            "start",
            "test",
            "procedure",
        ],
        "duration_units": [5.5, 4.5, None, 3.25, 1.75, 2.0],  # Float durations
    }
)

timesteps_pool = EventSequencePool(
    sequence_data=timestep_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestep",
        "entity_features": ["event_type", "duration_units"],
    },
)

# Declare duration with UNIT granularity (no conversion, preserves floats)
timesteps_pool.update_entity_metadata(
    feature_name="duration_units", feature_type="duration", granularity="unit"
)

print("Timestep-based events:")
timesteps_pool

# %%
# Convert to intervals using UNIT durations (float addition, no timedelta)
timestep_intervals = timesteps_pool.as_interval(duration="duration_units")

print("Timestep-based intervals (floats preserved):")
timestep_intervals

# %% [markdown]
# ## 5. Working with Metadata
#
# After conversion, always verify and update metadata as needed.

# %%
# Check metadata after conversion
print("Metadata after Event -> State conversion:")
print(states_pool.metadata.describe(verbose=True))

# %%
# Update metadata for a categorical feature
states_pool.update_entity_metadata(
    feature_name="location",
    feature_type="categorical",
    categories=["Emergency", "ICU", "Ward"],
)

print(states_pool.metadata.describe(verbose=True))
