"""
PAM Clustering (Partition Around Medoids)
==========================================

This example demonstrates how to perform PAM (Partition Around Medoids) clustering on sequence pools.
PAM is a robust clustering algorithm that selects actual data points as cluster centers (medoids).
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
    PAMClusterer,
    PAMClustererSettings,
)

# %% [markdown]
# ## 1. Data Initialization and Generation
#
# We generate synthetic event sequences to use as input for clustering.

# %%
NUM_SEQUENCES = 25
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
# ## 2. PAM Clustering with Default Settings
#
# PAM clustering minimizes the inertia by selecting actual sequences as medoids (cluster centers).
#
# .. important::
#     PAM precomputes the full distance matrix, which can be memory-intensive for large datasets.
#     For datasets with thousands of sequences, consider using CLARA instead.

# %%
# Initialize the PAM clusterer with 3 clusters
pam_settings = PAMClustererSettings(
    metric="linearpairwise",  # Sequence-level metric
    n_clusters=3,  # Number of clusters to form
    max_iter=100,  # Maximum iterations for optimization
    cluster_column="pam_cluster",  # Column where cluster labels will be stored
)

clusterer = PAMClusterer(settings=pam_settings)

# Show clusterer settings
clusterer.view_settings()

# %% [markdown]
# ## 3. Fit the Model
#
# Apply PAM clustering to the sequence pool.

# %%
# Fit the clusterer
clusterer.fit(event_pool)

# View cluster assignments
event_pool.static_data

# %% [markdown]
# ## 4. Access Medoids
#
# PAM selects actual sequences as medoids (representative sequences for each cluster).
# These medoids minimize the total distance to all sequences in their cluster.

# %%
# Get the medoid sequences
medoids = clusterer.medoids
print(f"Medoid IDs: {medoids}")

# View medoid sequences
for medoid_id in medoids:
    print(f"\nMedoid {medoid_id}:")
    print(event_pool[medoid_id].sequence_data)

# %% [markdown]
# ## 5. Custom Distance Metric
#
# You can use different distance metrics depending on your needs.

# %%
# Using Edit distance (Levenshtein) metric
pam_edit_settings = PAMClustererSettings(
    metric="edit",
    n_clusters=3,
    cluster_column="pam_edit_cluster",
)

clusterer_edit = PAMClusterer(settings=pam_edit_settings)
clusterer_edit.fit(event_pool)

# %%
# Access clustering results from the static data
event_pool.static_data

# %% [markdown]
# ## 6. PAM Clustering on Trajectory Pools
#
# PAM also works on trajectory pools. You need to use a trajectory-level metric.

# %%
# Initialize and populate a trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(event_pool, "events")

# Configure PAM for trajectories with appropriate metric
pam_traj_settings = PAMClustererSettings(
    metric="aggregation",  # Trajectory-level distance metric
    n_clusters=3,
    cluster_column="pam_traj_cluster",
)

clusterer_traj = PAMClusterer(settings=pam_traj_settings)
clusterer_traj.fit(trajectory_pool)

# View results
trajectory_pool.static_data
