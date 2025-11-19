"""
CLARA Clustering (Clustering LARge Applications)
=================================================

This example demonstrates how to perform CLARA clustering on large sequence pools.
CLARA is designed for large datasets and uses sampling to make PAM clustering scalable.
"""

# %% [markdown]
# ### Required Imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
)

# Trajectory pools
from tanat.trajectory import (
    TrajectoryPool,
)

# Clustering tools
from tanat.clustering import (
    CLARAClusterer,
    CLARAClustererSettings,
)

# %% [markdown]
# ## 1. Data Initialization and Generation
#
# For CLARA, we generate a larger dataset to demonstrate its scalability.
# CLARA is designed for datasets that would be too large for standard PAM.

# %%
NUM_SEQUENCES = 100  # Larger dataset
SEQUENCE_LENGTHS = [5, 6, 7, 8, 9, 10]
RANDOM_SEED = 42

# Generate synthetic event sequences
event_data = generate_event_sequences(
    n_seq=NUM_SEQUENCES,
    seq_size=SEQUENCE_LENGTHS,
    vocabulary=["A", "B", "C", "D", "E"],
    missing_data=0.0,
    entity_feature="event",
    seed=RANDOM_SEED,
)

# Define event sequence settings
event_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

event_pool = EventSequencePool(event_data, event_settings)
event_pool

# %% [markdown]
# ## 2. CLARA Clustering with Default Settings
#
# CLARA (Clustering LARge Applications) divides the dataset into multiple samples,
# applies PAM to each sample, and selects the best set of medoids.
#
# .. note::
#     CLARA is particularly useful when your dataset is too large to compute
#     the full distance matrix required by standard PAM.

# %%
# Initialize the CLARA clusterer
clara_settings = CLARAClustererSettings(
    metric="linearpairwise",  # Sequence-level metric
    n_clusters=3,  # Number of clusters to form
    sampling_ratio=0.4,  # Use 40% of data for each PAM run
    nb_pam_instances=5,  # Run 5 independent PAM instances
    max_iter=100,  # Maximum iterations per PAM run
    cluster_column="clara_cluster",  # Column where cluster labels will be stored
)

clusterer = CLARAClusterer(settings=clara_settings)

# Show clusterer settings
clusterer.view_settings()

# %% [markdown]
# ## 3. Understanding CLARA Parameters
#
# **Key parameters explained:**
#
# - ``sampling_ratio``: Fraction of data to sample for each PAM instance (default: 0.4)
# - ``nb_pam_instances``: Number of independent PAM runs with different samples (default: 5)
# - ``max_iter``: Maximum iterations for each PAM optimization

# %% [markdown]
# ## 4. Fit the Model
#
# Apply CLARA clustering to the sequence pool.

# %%
# Fit the clusterer
clusterer.fit(event_pool)

# View cluster assignments
event_pool.static_data

# %% [markdown]
# ## 5. Access Medoids
#
# Like PAM, CLARA selects actual sequences as medoids.
# The final medoids are chosen from the best PAM run.

# %%
# Get the medoid sequences
medoids = clusterer.medoids
print(f"Medoid IDs: {medoids}")

# View medoid sequences
for medoid_id in medoids:
    print(f"\nMedoid {medoid_id}:")
    print(event_pool[medoid_id].sequence_data)

# %% [markdown]
# ## 6. Tuning CLARA Parameters
#
# Adjust sampling and number of PAM instances for your dataset size.

# %%
# More aggressive sampling for very large datasets
clara_large_settings = CLARAClustererSettings(
    metric="edit",
    n_clusters=4,
    sampling_ratio=0.2,  # Smaller samples
    nb_pam_instances=10,  # More PAM runs for better coverage
    cluster_column="clara_large_cluster",
)

clusterer_large = CLARAClusterer(settings=clara_large_settings)
clusterer_large.fit(event_pool)

# %%
# Access clustering results from the static data
event_pool.static_data

# %% [markdown]
# ## 7. CLARA Clustering on Trajectory Pools
#
# CLARA also works on trajectory pools. You need to use a trajectory-level metric.

# %%
# Initialize and populate a trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(event_pool, "events")

# Configure CLARA for trajectories with appropriate metric
clara_traj_settings = CLARAClustererSettings(
    metric="aggregation",  # Trajectory-level distance metric
    n_clusters=3,
    sampling_ratio=0.3,
    nb_pam_instances=5,
    cluster_column="clara_traj_cluster",
)

clusterer_traj = CLARAClusterer(settings=clara_traj_settings)
clusterer_traj.fit(trajectory_pool)

# View results
trajectory_pool.static_data
