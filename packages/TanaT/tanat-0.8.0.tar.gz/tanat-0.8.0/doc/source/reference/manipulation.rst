.. _manipulation_reference

======================
Data Manipulation API
======================

This page provides a comprehensive overview of data manipulation methods available across different TanaT objects.

.. role:: green
.. role:: red
.. role:: blue

.. contents:: Table of Contents
   :local:
   :depth: 2
   :hidden: 

Overview
========

TanaT provides a rich set of manipulation methods for temporal data analysis.
This reference shows which methods are available for each object type.

**Legend:**

* :green:`✓` : Method available
* :red:`✗` : Method not available
* :blue:`✓\*` : Accepts optional ``sequence_name`` parameter (Trajectory/TrajectoryPool)

Method Compatibility Matrix
============================

Position-based Selection
------------------------

Methods for selecting entities by their position/rank in sequences.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``head(n)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`
   * - ``tail(n)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`
   * - ``slice(start, end, step)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`
   * - ``[index]``
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
     - :red:`✗`
   * - ``[start:end:step]``
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
     - :red:`✗`

:blue:`✓\*` Optional ``sequence_name`` parameter for Trajectory/TrajectoryPool objects. Applies to all sequences if not specified.

**Method Descriptions:**

``head(n)``
    Get first ``n`` entities. Negative values return all except last ``|n|`` entities.
    For Trajectory/TrajectoryPool: use ``sequence_name`` parameter to target specific sequence.

``tail(n)``
    Get last ``n`` entities. Supports negative values to get all except first ``|n|``.
    For Trajectory/TrajectoryPool: use ``sequence_name`` parameter to target specific sequence.

``slice(start, end, step)``
   Select entities by position range with optional step for sampling.
   Supports negative indices. For Trajectory/TrajectoryPool: use ``sequence_name`` parameter to target specific sequence.

``[index]``
   Python-style single index access. Returns Entity object (Sequence only).

``[start:end:step]``
   Python-style slice notation. Returns new Sequence (Sequence only).

**Examples:**

.. code-block:: python

   # Sequence - Get first 10 entities
   first_10 = sequence.head(10)
   
   # Sequence - Get all except last 2
   all_but_last_2 = sequence.head(-2)
   
   # SequencePool - Apply to all sequences
   pool_first_5 = pool.head(5)
   
   # Trajectory - Specific sequence
   traj_first = trajectory.head(10, sequence_name="prescriptions")
   
   # Slicing with step
   every_second = sequence.slice(step=2)
   positions_10_to_50 = sequence.slice(start=10, end=50)
   
   # Python indexing (Sequence only)
   first_entity = sequence[0]
   last_entity = sequence[-1]
   subset = sequence[10:50:2]  # start:end:step

Filtering & Selection
---------------------

Methods for conditional selection and filtering.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``filter(criterion)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`
   * - ``subset(ids)``
     - :red:`✗`
     - :green:`✓`
     - :red:`✗`
     - :green:`✓`
   * - ``which(criterion)``
     - :red:`✗`
     - :green:`✓`
     - :red:`✗`
     - :green:`✓`
   * - ``match(criterion)``
     - :green:`✓`
     - :red:`✗`
     - :green:`✓`
     - :red:`✗`

:blue:`\*` Optional ``sequence_name`` parameter for Trajectory objects (applies to all sequences if not specified).

**Method Descriptions:**

``filter(criterion)``
   Apply filtering criterion at entity or sequence or trajectory level.
   Use ``sequence_name`` parameter to specify entity/sequence level filtering from Trajectory/TrajectoryPool.

``subset(ids)``
   Extract subset by sequence IDs. Available for Pool objects only.

``which(criterion)``
   Get IDs of sequences/trajectories matching criterion. Available for pool only.

``match(criterion)``
   Test if sequence/trajectory matches criterion, returns boolean.

**Examples:**

.. code-block:: python

   # Entity-level filtering with query
   from tanat.criterion.mixin.query.settings import QueryCriterion
   
   criterion = QueryCriterion(query="event_type == 'EMERGENCY'")
   filtered = sequence.filter(criterion)
   
   # Pool - filter sequences by length
   from tanat.criterion.sequence.type.length.settings import LengthCriterion
   
   length_criterion = LengthCriterion(gt=10)
   long_sequences = pool.filter(length_criterion, level="sequence")
   
   # Pool - get IDs matching criterion
   matching_ids = pool.which(length_criterion)
   
   # Pool - subset by IDs
   subset_pool = pool.subset(["seq-1", "seq-3", "seq-5"])
   
   # Trajectory filtering (specific sequence)
   rank_criterion = {"start": 0, "end": 50}
   traj_filtered = trajectory.filter(
       rank_criterion,
       sequence_name="prescriptions",
       criterion_type="rank"
   )

Temporal Alignment
------------------

Methods for setting temporal reference point (T0).

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``zero_from_query(query)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`
   * - ``zero_from_position(pos)``
     - :green:`✓`
     - :green:`✓`
     - :blue:`✓\*`
     - :blue:`✓\*`

:blue:`\*` ``sequence_name`` parameter behavior differs by method (see descriptions below).

**Method Descriptions:**

``zero_from_query(query)``
   Set T0 from query on sequence data.
   For Trajectory/TrajectoryPool: **requires** ``sequence_name`` parameter to specify which sequence to query.

``zero_from_position(pos)``
   Set T0 from entity position (0-based indexing).
   For Trajectory/TrajectoryPool: **optional** ``sequence_name`` parameter. If ``None``, uses position across all sequences.

**Examples:**

.. code-block:: python

   # Sequence - Set T0 from query
   sequence.zero_from_query("event_type == 'DIAGNOSIS'")
   
   # Sequence - Set T0 from position (5th entity)
   sequence.zero_from_position(4)  # 0-based indexing
   
   # SequencePool - applies to all sequences
   pool.zero_from_query("medication == 'INSULIN'")
   
   # Trajectory - query REQUIRES sequence_name
   trajectory.zero_from_query(
       "event_type == 'ADMISSION'",
       sequence_name="hospital_events"  # Required!
   )
   
   # Trajectory - position with specific sequence
   trajectory.zero_from_position(0, sequence_name="prescriptions")
   
   # Trajectory - position across ALL sequences (sequence_name=None)
   trajectory.zero_from_position(10)  # Uses 10th entity across all sequences

Temporal Transformations
------------------------

Methods for temporal data transformations.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``to_relative_time()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``to_relative_rank()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``to_time_spent()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``to_occurrence()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`

**Method Descriptions:**

``to_relative_time()``
   Convert timestamps to time relative to T0. Requires T0 to be set.

``to_relative_rank()``
   Convert positions to ranks relative to T0 entity.

``to_time_spent()``
   Compute time spent in each state/interval.
   Available for StateSequence and IntervalSequence only.

``to_occurrence()``
   Count occurrences of events/states up to each position.

**Examples:**

.. code-block:: python

   # Convert to relative time (requires T0)
   sequence.zero_from_position(0)
   relative_sequence = sequence.to_relative_time()
   
   # Convert to relative ranks
   ranked_sequence = sequence.to_relative_rank()
   
   # Time spent in each state (StateSequence)
   state_sequence.to_time_spent()
   
   # Count occurrences
   event_sequence.to_occurrence()

Type Conversion
---------------

Methods for converting between sequence types.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``as_event()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``as_interval()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``as_state()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`

**Method Descriptions:**

``as_event()``
   Convert to EventSequence(Pool).

``as_interval()``
   Convert to IntervalSequence(Pool).

``as_state()``
   Convert to StateSequence(Pool).

**Examples:**

.. code-block:: python

   # Convert interval to event (takes start time)
   event_sequence = interval_sequence.as_event()
   
   # Convert event to interval (requires end time strategy)
   interval_sequence = event_sequence.as_interval()
   
   # Convert interval to state
   state_sequence = interval_sequence.as_state()

Feature Engineering
-------------------

Methods for adding or removing features.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``add_entity_feature()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``drop_entity_feature()``
     - :green:`✓`
     - :green:`✓`
     - :red:`✗`
     - :red:`✗`
   * - ``add_static_features()``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
   * - ``drop_static_feature()``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`

**Method Descriptions:**

``add_entity_feature()``
   Add computed entity-level feature to sequence data.

``drop_entity_feature()``
   Remove entity-level feature from sequence data.

``add_static_features()``
   Add computed static (sequence-level) feature from external data.

``drop_static_feature()``
   Remove static feature.

**Examples:**

.. code-block:: python

   # Add entity feature
    sequence.add_entity_feature(
        "posology_mg", values = [100, 200, 150, ...]
    )
   
    # Add static feature
    pool.add_static_features(
        static_data=df_static, 
        id_column="patient_id",
        static_features=["age", "gender"],
        override=False
    )
   
   # Drop features
   sequence.drop_entity_feature("posology_mg")
   pool.drop_static_feature("age")

Descriptive Statistics
------------------

Methods for computing descriptive statistics.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``describe()``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
   * - ``statistics``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`

**Method Descriptions:**

``describe()``
   Statistical description of sequence data in pandas-style format (DataFrame).
   Includes length, vocabulary size, entropy, and other metrics.

``statistics``
   Property that computes key statistics as a dictionary.
   For Trajectory objects, automatically prefixes sequence-specific stats (e.g., ``diagnosis_length``).

**Examples:**

.. code-block:: python

   # Statistical description (DataFrame)
   desc_df = sequence.describe()
   print(desc_df)

   # Add description to static data
   desc_df = sequence.describe(add_to_static=True)
   print(sequence.static_data) # desc_df merged to static
   
   # Object statistics (dict)
   stats = sequence.statistics
   print(f"Length: {stats['length']}")
   print(f"Vocabulary: {stats['vocab_size']}")
   
   # Pool statistics
   pool_stats = pool.statistics
   print(f"Total sequences: {pool_stats['total_sequences']}")
   print(f"Avg length: {pool_stats['avg_length']:.1f}")
   
   # Trajectory statistics (prefixed by sequence name)
   traj_stats = trajectory.statistics
   print(f"Diagnosis length: {traj_stats['diagnosis_length']}")
   print(f"Medication vocab: {traj_stats['medication_vocab_size']}")

Copy & Modification
-------------------

Methods for copying and in-place modifications.

.. list-table::
   :header-rows: 1
   :widths: 35 15 15 18 17

   * - Method
     - Sequence
     - SequencePool
     - Trajectory
     - TrajectoryPool
   * - ``copy(deep=True)``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
   * - ``inplace=True``
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`
     - :green:`✓`

**Method Descriptions:**

``copy(deep=True)``
   Create a copy of the object. Use ``deep=False`` for shallow copy.

``inplace=True``
   Most manipulation methods support ``inplace=True`` parameter to modify the object in place
   instead of returning a new copy.

**Examples:**

.. code-block:: python

   # Create copy
   sequence_copy = sequence.copy()
   
   # In-place modification
   sequence.head(10, inplace=True)  # Modifies sequence directly
   pool.filter(criterion, inplace=True)  # Modifies pool directly

Notes on Trajectory-specific Behavior
======================================

Methods marked with :blue:`✓\*` for Trajectory objects accept additional parameters:

``sequence_name`` Parameter (Optional)
--------------------------------------

Many methods that operate on sequences accept an optional ``sequence_name`` argument to specify which sequence to operate on.

.. code-block:: python

   # Position-based selection
   trajectory.head(10, sequence_name="prescriptions")
   trajectory.tail(5, sequence_name="events")
   trajectory.slice(start=0, end=50, sequence_name="events")
   
   # Filtering entity within `events` sequence
   trajectory.filter(
       criterion={"event_type": "EMERGENCY"},
       sequence_name="events",
       criterion_type="query"
       level="entity"
   )
   
   # Temporal alignment
   trajectory.zero_from_query(
       "medication == 'INSULIN'",
       sequence_name="prescriptions"
   )
   
   # TrajectoryPool - same pattern
   pool.head(10, sequence_name="prescriptions")

Apply to All Sequences
----------------------

**Most methods** (``head``, ``tail``, ``slice``, ``filter``, ``zero_from_position``) support ``sequence_name=None`` 
to apply the operation to **all sequences** simultaneously:

.. code-block:: python

   # Apply to all sequences
   trajectory.head(10)  # Apply head(10) to all sequences
   trajectory.tail(5)   # Apply tail(5) to all sequences
   trajectory.zero_from_position(0)  # Set T0 at first entity across all sequences
   
   # TrajectoryPool
   pool.slice(start=0, end=20)  # Apply to all sequences in all trajectories

**Exception:** ``zero_from_query`` always requires an explicit ``sequence_name`` because queries are sequence-specific:

.. code-block:: python

   # This is REQUIRED - cannot query across all sequences
   trajectory.zero_from_query(
       query="event_type == 'ADMISSION'",
       sequence_name="events"  # Must specify which sequence to query
   )

See Also
========

* :doc:`criterion` - Filtering criteria reference
* :doc:`alignment` - Temporal alignment details
* :doc:`metadata` - Metadata management
* :doc:`/user-guide/auto_examples/index` - Examples gallery
* :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_sequence` - Tutorial for sequence data wrangling
* :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_trajectory` - Tutorial for trajectory data wrangling

API Reference
=============

For detailed API documentation of each method, see:

* :py:class:`tanat.mixin.manipulation.data.sequence` - Sequence manipulation methods
* :py:class:`tanat.criterion` - Criterion system for filtering
