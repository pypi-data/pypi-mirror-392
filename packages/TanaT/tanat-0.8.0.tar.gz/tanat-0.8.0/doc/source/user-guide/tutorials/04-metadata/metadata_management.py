# %% [markdown]
# .. _metadata_tutorial:
#
# # Metadata Management
#
# This tutorial demonstrates how to work with metadata in *TanaT*. Metadata describes the structure and types of your temporal data, enabling proper type coercion, validation, and analysis.
#
# **Learning Objectives:**
# - Understand automatic metadata inference (default behavior)
# - Inspect and validate inferred metadata
# - Correct inference errors using update methods
# - Provide explicit metadata for advanced control
# - Ensure metadata coherence across sequences and trajectories

# %% [markdown]
# ## Required Imports
#
# We'll use TanaT's sequence and trajectory components along with some utilities for visualization.

# %%
from datetime import datetime
import pandas as pd

# TanaT sequence pools
from tanat.sequence import EventSequencePool

# TanaT trajectory pool
from tanat.trajectory import TrajectoryPool

# %% [markdown]
# ## 1. Automatic Metadata Inference
#
# TanaT automatically infers metadata from your data when you create sequence pools. This is the default behavior and requires no configuration.
#
# Let's create a simple dataset of patient visits and see what metadata TanaT infers:

# %%
# Create a simple healthcare dataset
data = pd.DataFrame(
    {
        "patient_id": [101, 101, 101, 102, 102],
        "timestamp": [
            datetime(2023, 1, 10, 9, 0),
            datetime(2023, 1, 17, 14, 30),
            datetime(2023, 2, 5, 10, 15),
            datetime(2023, 1, 12, 11, 0),
            datetime(2023, 1, 20, 16, 45),
        ],
        "event_type": [
            "consultation",
            "lab_test",
            "consultation",
            "consultation",
            "lab_test",
        ],
        "department": [
            "cardiology",
            "laboratory",
            "cardiology",
            "neurology",
            "laboratory",
        ],
    }
)

# Create an EventSequencePool without specifying metadata
# TanaT will infer everything automatically
visits_pool = EventSequencePool(
    sequence_data=data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["event_type", "department"],
    },
)

print("EventSequencePool created successfully!")
print(f"Number of patients: {len(visits_pool)}")
print(f"Total visits: {len(data)}")

# %% [markdown]
# ### What metadata was inferred?
#
# The `.metadata` attribute contains all the inferred information about temporal and entity features:

# %%
# Access the metadata object
visits_pool.metadata

# %% [markdown]
# ## 2. Inspecting Metadata
#
# TanaT provides convenient methods to inspect metadata in human-readable formats:
#
# - `.metadata.view()`: Display metadata as YAML with documentation.
# - `.metadata.describe()`: Display metadata with descriptions (human-friendly)

# %%
# Describe metadata with human-readable explanations
print("Human-Readable Description:")
print(visits_pool.metadata.describe(verbose=False))
print("\n" + "=" * 60 + "\n")
# View metadata as YAML
print("YAML Representation:")
visits_pool.metadata.view()

# %% [markdown]
# ## 3. Correcting Inference Errors
#
# Sometimes automatic inference might not match your requirements. TanaT provides update methods to correct metadata after creation.
#
# ### Example: Updating Temporal Metadata
#
# Let's say we want to change the timezone setting for our timestamps:

# %%
# Update temporal metadata with a specific timezone
visits_pool.update_temporal_metadata(timezone="Europe/Paris")
print(visits_pool.metadata.describe(verbose=True))

# %%
# You can also update the date format
visits_pool.update_temporal_metadata(format="%Y-%m-%d %H:%M")
print(visits_pool.metadata.describe(verbose=True))

# %% [markdown]
# ### Example: Updating Entity Metadata
#
# We can also correct metadata for entity features (features that vary within sequences):

# %%
# Let's say we want to specify that department is an ordinal feature
# with a specific order
visits_pool.update_entity_metadata(
    feature_name="department",
    feature_type="categorical",
    categories=["laboratory", "cardiology", "neurology", "emergency"],
    ordered=True,
)

print(visits_pool.metadata.describe(verbose=True))

# %% [markdown]
# ### Method Chaining
#
# Update methods return `self`, allowing you to chain multiple updates:

# %%
# Chain multiple updates together
# fmt: off
visits_pool.update_temporal_metadata(timezone="UTC") \
            .update_entity_metadata(
                feature_name="event_type",
                feature_type="categorical",
                categories=["consultation", "lab_test", "surgery", "emergency"],
            )
# fmt: on
print(visits_pool.metadata.describe(verbose=True))

# %% [markdown]
# ### Changing Temporal Type
#
# You can even change the temporal type entirely. For example, converting from datetime to timestep:

# %%
# Create a simple timestep-based dataset
timestep_data = pd.DataFrame(
    {
        "patient_id": [201, 201, 201, 202, 202],
        "timestep": [1, 5, 10, 2, 8],
        "measurement": ["BP", "HR", "BP", "BP", "HR"],
        "value": [120, 75, 118, 130, 82],
    }
)

# Create pool and then change from default datetime to timestep
measurements_pool = EventSequencePool(
    sequence_data=timestep_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestep",
        "entity_features": ["measurement", "value"],
    },
)

# Update to timestep with appropriate settings
measurements_pool.update_temporal_metadata(
    temporal_type="timestep", min_value=1, max_value=100
)
print(measurements_pool.metadata.describe(verbose=True))

# %% [markdown]
# ## 4. Specifying Metadata Explicitly (Advanced)
#
# Instead of relying on inference, you can provide metadata explicitly at initialization. This is useful when:
# - You know the exact metadata structure you need
# - You want to avoid inference overhead
# - You need to ensure specific settings from the start

# %%
# Define explicit metadata
explicit_metadata = {
    "temporal_descriptor": {
        "temporal_type": "datetime",
        "granularity": "second",
        "settings": {
            "timezone": "America/New_York",
            "date_format": "%Y-%m-%d %H:%M:%S",
        },
    },
    "entity_descriptors": {
        "event_type": {
            "feature_type": "categorical",
            "settings": {
                "categories": ["consultation", "lab_test", "surgery"],
            },
        },
        "department": {
            "feature_type": "categorical",
            "settings": {
                "categories": ["cardiology", "neurology", "emergency"],
            },
        },
    },
}

# Create pool with explicit metadata
explicit_pool = EventSequencePool(
    sequence_data=data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["event_type", "department"],
    },
    metadata=explicit_metadata,
)

# Pool overview
explicit_pool

# %% [markdown]
# ## 5. Sequence vs Trajectory Level Metadata
#
# **Critical distinction:** TanaT has two levels of data organization:
# - **Sequence level**: Individual sequences (e.g., one patient's journey)
# - **Trajectory level**: Collections of sequences (e.g., multiple patients)
#
# Metadata updates behave differently at each level!

# %% [markdown]
# ### Sequence-level updates
#
# When you update metadata on a **sequence pool**, you're updating metadata for all sequences in that pool:

# %%
# Sequence-level update affects all sequences in the pool
visits_pool.update_temporal_metadata(timezone="Europe/London")

# Access sequence within the pool
print(visits_pool[101].metadata.describe(verbose=True))

# %% [markdown]
# ### Trajectory-level updates and propagation
#
# When you update metadata on a **trajectory pool**, the changes **automatically propagate** to all contained sequence pools:
#
# This ensures **metadata coherence** across the entire trajectory.

# %%
# Create a second sequence pool (medications)
meds_data = pd.DataFrame(
    {
        "patient_id": [101, 101, 102, 102],
        "timestamp": [
            datetime(2023, 1, 10, 10, 0),
            datetime(2023, 1, 17, 15, 0),
            datetime(2023, 1, 12, 12, 0),
            datetime(2023, 1, 20, 17, 0),
        ],
        "medication": ["aspirin", "metformin", "aspirin", "lisinopril"],
        "dosage": [100, 500, 100, 10],
    }
)

medications_pool = EventSequencePool(
    sequence_data=meds_data,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["medication", "dosage"],
    },
)

# Create a trajectory pool combining visits and medications
trajectory = TrajectoryPool(
    sequence_pools={"visits": visits_pool, "medications": medications_pool}
)


# Pool overview
trajectory

# %%
# Update temporal metadata at TRAJECTORY level
# This will propagate to ALL sequence pools
trajectory.update_temporal_metadata(timezone="Asia/Tokyo")

# Check updated timezones in both pools
print("Visits Sequence Metadata:", "\n--------------------")
print(trajectory.sequence_pools["visits"].metadata.describe(verbose=True))
print("\n\nMedications Sequence Metadata:", "\n--------------------")
print(trajectory.sequence_pools["medications"].metadata.describe(verbose=True))

# %% [markdown]
# ### Static metadata (trajectory-specific features)
#
# Static features exist at the **trajectory level** (they don't vary within sequences). Examples: patient age, gender, diagnosis at baseline.

# %%
# Add static data to trajectory
static_data = pd.DataFrame(
    {"patient_id": [101, 102], "age": [45, 62], "gender": ["M", "F"]}
)

trajectory_with_static = TrajectoryPool(
    sequence_pools={"visits": visits_pool, "medications": medications_pool},
    static_data=static_data,
    settings={
        "id_column": "patient_id",
        "static_features": ["age", "gender"],
    },
)

# Update static metadata
trajectory_with_static.update_static_metadata(
    feature_name="gender",
    feature_type="categorical",
    categories=["M", "F", "Other"],
)

print(trajectory_with_static.metadata.describe(verbose=True))

# %% [markdown]
# ## 6. Complete Healthcare Example
#
# Let's put it all together with a realistic healthcare scenario: tracking patient journeys through a hospital system.

# %%
# Step 1: Create comprehensive patient event data
patient_events = pd.DataFrame(
    {
        "patient_id": [1001, 1001, 1001, 1001, 1002, 1002, 1002, 1003, 1003],
        "timestamp": [
            datetime(2023, 6, 1, 9, 0),
            datetime(2023, 6, 3, 14, 30),
            datetime(2023, 6, 10, 11, 15),
            datetime(2023, 6, 15, 16, 45),
            datetime(2023, 6, 2, 10, 30),
            datetime(2023, 6, 8, 13, 0),
            datetime(2023, 6, 20, 9, 30),
            datetime(2023, 6, 5, 8, 45),
            datetime(2023, 6, 12, 15, 0),
        ],
        "event": [
            "admission",
            "surgery",
            "consultation",
            "discharge",
            "admission",
            "lab_test",
            "discharge",
            "admission",
            "emergency",
        ],
        "department": [
            "emergency",
            "surgery",
            "cardiology",
            "discharge_unit",
            "cardiology",
            "laboratory",
            "discharge_unit",
            "neurology",
            "emergency",
        ],
        "severity": [3, 4, 2, 1, 2, 1, 1, 5, 5],
    }
)

# Step 2: Create medication events
medication_events = pd.DataFrame(
    {
        "patient_id": [1001, 1001, 1001, 1002, 1002, 1003],
        "timestamp": [
            datetime(2023, 6, 1, 10, 0),
            datetime(2023, 6, 3, 18, 0),
            datetime(2023, 6, 10, 12, 0),
            datetime(2023, 6, 2, 11, 0),
            datetime(2023, 6, 8, 14, 30),
            datetime(2023, 6, 5, 9, 0),
        ],
        "medication": [
            "morphine",
            "antibiotic",
            "aspirin",
            "metformin",
            "aspirin",
            "morphine",
        ],
        "dosage_mg": [10, 500, 100, 1000, 100, 15],
        "route": ["IV", "oral", "oral", "oral", "oral", "IV"],
    }
)

# Step 3: Create static patient data
patient_demographics = pd.DataFrame(
    {
        "patient_id": [1001, 1002, 1003],
        "age": [54, 68, 72],
        "gender": ["M", "F", "M"],
        "diagnosis": ["cardiac_event", "diabetes", "stroke"],
    }
)

print("Created comprehensive healthcare dataset!")
print(f"Clinical events: {len(patient_events)}")
print(f"Medication events: {len(medication_events)}")
print(f"Patients: {len(patient_demographics)}")

# %%
# Step 4: Create sequence pools with automatic inference
clinical_pool = EventSequencePool(
    sequence_data=patient_events,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["event", "department", "severity"],
    },
)

medication_pool = EventSequencePool(
    sequence_data=medication_events,
    settings={
        "id_column": "patient_id",
        "time_column": "timestamp",
        "entity_features": ["medication", "dosage_mg", "route"],
    },
)


print("Sequence pools created with automatic metadata inference!")
print("\nClinical pool metadata:")
print(clinical_pool.metadata.describe())
print("\n" + "=" * 60)
print("\nMedication pool metadata:")
print(medication_pool.metadata.describe())

# %%
# Step 5: Correct metadata after inspection

# fmt: off
# -- clinical pool updates
clinical_pool.update_entity_metadata(
                feature_name="severity", # correcting severity to ordinal categorical
                feature_type="categorical",
                categories=[1, 2, 3, 4, 5],
                ordered=True,
            ) \
            .update_temporal_metadata(
                timezone="America/New_York"
            )

## -- medication pool updates
medication_pool.update_entity_metadata(
                    feature_name="dosage_mg", # correcting dosage to ordinal categorical
                    feature_type="categorical",
                    categories=[10, 15, 100, 500, 1000],
                    ordered=True,
                ) \
                .update_temporal_metadata(
                    timezone="America/New_York"
                )
# fmt: on

# %%
# Step 6: Create trajectory with static features
patient_trajectory = TrajectoryPool(
    sequence_pools={"clinical_events": clinical_pool, "medications": medication_pool},
    static_data=patient_demographics,
    settings={
        "id_column": "patient_id",
        "static_features": ["age", "gender", "diagnosis"],
    },
)

# fmt: off
# Update static metadata
patient_trajectory.update_static_metadata(
                    feature_name="gender",
                    feature_type="categorical",
                    categories=["M", "F", "Other"],
                ) \
                .update_static_metadata(
                    feature_name="diagnosis",
                    feature_type="categorical",
                    categories=[
                        "cardiac_event",
                        "diabetes",
                        "stroke",
                        "respiratory",
                        "other",
                    ],
                )
# fmt: on

print(patient_trajectory.metadata.describe(verbose=True))

# %%
# Step 7: Demonstrate trajectory-level propagation
# Update timezone at trajectory level - it propagates to all sequence pools
patient_trajectory.update_temporal_metadata(
    timezone="UTC",
)

print("Trajectory level:", "\n----------------")
print(patient_trajectory.metadata.describe(verbose=True))
print("\n\nClinical pool level:", "\n----------------")
print(
    patient_trajectory.sequence_pools["clinical_events"].metadata.describe(verbose=True)
)
print("\n\nMedication pool level:", "\n----------------")
print(patient_trajectory.sequence_pools["medications"].metadata.describe(verbose=True))
