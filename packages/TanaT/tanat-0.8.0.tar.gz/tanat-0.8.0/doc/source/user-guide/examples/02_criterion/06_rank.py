"""
Rank criterion
==================

Filtering entities based on their position/rank in sequences using both direct
criterion API and convenient helper methods (head, tail, slice).
"""

# %% [markdown]
# ### Required imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import generate_event_sequences

# Sequence pools
from tanat.sequence import EventSequencePool

# Trajectory pools
from tanat.trajectory import TrajectoryPool

# Rank-based filtering criterion
from tanat.criterion import RankCriterion

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset to demonstrate rank-based filtering.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [8, 9, 10, 11, 12]
SEED = 42

simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

simple_pool = EventSequencePool(simple_data, simple_settings)
simple_pool

# %% [markdown]
# ## 2. Helper Methods (Recommended)
#
# The easiest way to use rank-based filtering is through the helper methods:
# ``head()``, ``tail()``, and ``slice()``. These methods provide a clean,
# intuitive API for position-based selection.

# %% [markdown]
# ### Using head() - Get first N entities

# %%
# Get first 5 entities from each sequence
first_5 = simple_pool.head(5)
first_5

# %%
# Negative values: get all EXCEPT last N entities
all_but_last_2 = simple_pool.head(-2)
all_but_last_2

# %% [markdown]
# ### Using tail() - Get last N entities

# %%
# Get last 3 entities from each sequence
last_3 = simple_pool.tail(3)
last_3

# %%
# Negative values: get all EXCEPT first N entities
all_but_first_2 = simple_pool.tail(-2)
all_but_first_2

# %% [markdown]
# ### Using slice() - Position range with optional step

# %%
# Select entities from position 2 to 7
middle_entities = simple_pool.slice(start=2, end=7)
middle_entities

# %%
# Sample every 2nd entity
every_second = simple_pool.slice(step=2)
every_second

# %%
# Combine: positions 1 to 8, every 2nd entity
sampled_range = simple_pool.slice(start=1, end=8, step=2)
sampled_range

# %%
# Using negative indices (Python-style)
last_five = simple_pool.slice(start=-5, end=None)
last_five

# %% [markdown]
# ## 3. Direct RankCriterion API (Advanced)
#
# For more complex scenarios or when you need programmatic control,
# you can use the RankCriterion directly.

# %% [markdown]
# ### Using first/last parameters

# %%
# Get first 5 entities using criterion
rank_criterion = RankCriterion(first=5)
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %%
# Get last 3 entities using criterion
rank_criterion = RankCriterion(last=3)
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %% [markdown]
# ### Using start/end parameters

# %%
# Select entities from position 2 to 7
rank_criterion = RankCriterion(start=2, end=7)
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %%
# Add step for sampling
rank_criterion = RankCriterion(start=0, end=10, step=2)
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %% [markdown]
# ### Using specific ranks

# %%
# Select specific positions (0-based indexing)
rank_criterion = RankCriterion(ranks=[0, 2, 4, 6])
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %%
# Negative ranks (from end: -1 = last, -2 = second to last)
rank_criterion = RankCriterion(ranks=[-1, -2, -3])
filtered_pool = simple_pool.filter(rank_criterion, level="entity")
filtered_pool

# %% [markdown]
# ## 4. Single Sequence Operations
#
# Helper methods work seamlessly with individual sequences.

# %%
single_seq = simple_pool["seq-0"]
print(f"Original sequence length: {len(single_seq)}")

# %%
# Head method on single sequence
first_3 = single_seq.head(3)
print(f"After head(3): {len(first_3)} entities")
first_3

# %%
# Tail method on single sequence
last_4 = single_seq.tail(4)
print(f"After tail(4): {len(last_4)} entities")
last_4

# %%
# Slice method on single sequence
middle = single_seq.slice(start=2, end=6)
print(f"After slice(start=2, end=6): {len(middle)} entities")
middle

# %%
# Python-style indexing also works!
first_entity = single_seq[0]
last_entity = single_seq[-1]
sliced = single_seq[1:5:2]  # start:end:step
print(f"Python indexing [1:5:2]: {len(sliced)} entities")

# %% [markdown]
# ## 5. Trajectory Operations
#
# Helper methods support trajectory-specific operations with the
# ``sequence_name`` parameter.

# %%
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")
trajectory_pool

# %% [markdown]
# ### Targeting specific sequences

# %%
# Get first 5 entities from 'events' sequence
filtered_traj = trajectory_pool.head(5, sequence_name="events")
filtered_traj

# %%
# Slice with step on specific sequence
sampled_traj = trajectory_pool.slice(start=0, end=8, step=2, sequence_name="events")
sampled_traj

# %% [markdown]
# ### Applying to all sequences

# %%
# When sequence_name is None (default), applies to ALL sequences
all_sequences_head = trajectory_pool.head(4)
all_sequences_head

# %% [markdown]
# ### Using direct criterion API for trajectories

# %%
# For programmatic control, use filter with RankCriterion
rank_criterion = RankCriterion(first=6)
filtered_traj = trajectory_pool.filter(
    rank_criterion, level="entity", sequence_name="events"
)
filtered_traj

# %% [markdown]
# ## 6. Relative Mode (T0-based positioning)
#
# RankCriterion supports relative mode for T0-aligned sequences.
# This is useful when working with temporal reference points.

# %%
# Set T0 for sequences (using third entity as reference)
pool_with_t0 = simple_pool.copy()
pool_with_t0.zero_from_position(3)

# %%
# Use relative ranks (relative to T0 entity)
rank_criterion = RankCriterion(start=-2, end=3, relative=True)
relative_filtered = pool_with_t0.filter(rank_criterion, level="entity")
relative_filtered

# %%
# Slice method also supports relative mode (positions relative to T0)
relative_filtered = pool_with_t0.slice(start=-2, end=3, relative=True)
relative_filtered
