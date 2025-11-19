.. _criterion_reference:

========================
Data Filtering Criterion
========================

Reference documentation for TanaT's criterion system for filtering and selecting temporal data.

Overview
========

Criterion provide a flexible and composable system for filtering sequences, trajectories, and their entities.
They enable:

* **Cohort selection**: Extract patient subgroups based on clinical criteria
* **Data cleaning**: Remove invalid or incomplete records
* **Pattern detection**: Find specific temporal patterns
* **Window extraction**: Select time-bounded data segments

All criterion support **method chaining** with filtering levels (entity/sequence/trajectory).

Filtering Levels
================

TanaT supports three hierarchical filtering levels:

**Entity-level**
   Filters individual records (events, states, intervals) within sequences.
   Preserves sequence structure but only includes matching entities.

**Sequence-level**
   Filters entire sequences based on whether they contain matching entities.
   Maintains complete sequence context (all entities kept or none).

**Trajectory-level**
   Filters trajectories based on whether they match the specified criteria.
   Available only for TrajectoryPool operations.

.. note::
   - Not all criterion support all filtering levels. See compatibility table below.
   - Entity-level filters are not allowed for StateSequence (will break the continuous nature of states).

Criterion Types
===============

QueryCriterion
--------------

Pandas-style query filtering on entity attributes.

**Signature:**

.. code-block:: python

    from tanat.criterion import QueryCriterion
    
    QueryCriterion(query: str)

**Parameters:**

* ``query``: Pandas query expression (uses ``DataFrame.query()`` syntax)

**Filtering Level Compatibility:**

.. list-table::
   :header-rows: 1

   * - Level
     - Support
     - Behavior
   * - Entity
     - Yes
     - Filters entities matching the query
   * - Sequence
     - Yes
     - Keeps sequences containing at least one matching entity
   * - Trajectory
     - Partial
     - Not directly supported. However, sequence-level filters can be propagated 
       to trajectory level when applied with ``intersection=True``, keeping 
       trajectories that contain a matching sequence

**Examples:**

.. code-block:: python

    # Simple equality
    criterion = QueryCriterion(query="visit_type == 'EMERGENCY'")
    
    # Numeric comparison
    criterion = QueryCriterion(query="age > 65")
    
    # Multiple conditions
    criterion = QueryCriterion(
        query="age > 65 and chronic_condition == True"
    )
    
    # Using 'in' operator
    criterion = QueryCriterion(
        query="visit_type in ['SPECIALIST', 'EMERGENCY']"
    )
    
    # String operations
    criterion = QueryCriterion(query="diagnosis.str.contains('DIABETES')")
    
    # Missing value detection
    criterion = QueryCriterion(query="feature.isna()")
    criterion = QueryCriterion(query="feature.notna()")

**Use cases:**

* Value-based filtering (specific events, categories, numeric ranges)
* Multi-condition cohort selection
* Missing data identification and removal
* Complex logical expressions

PatternCriterion
----------------

Sequential pattern matching on entity values.

**Signature:**

.. code-block:: python

    from tanat.criterion import PatternCriterion
    
    PatternCriterion(
        pattern:Dict[str, Union[str, List[str]]],
        contains: bool = False,
        case_sensitive: bool = True,
        operator: str = "and/or",
    )

**Parameters:**

* ``pattern``: Dictionary mapping feature names to values or sequences

  * Single value: ``{"feature": "VALUE"}``
  * Sequential pattern: ``{"feature": ["VALUE1", "VALUE2"]}``
  * Regex pattern: ``{"feature": "regex:^PATTERN"}``

* ``contains``: If True, pattern can occur anywhere. If False, pattern will exclude the match.
* ``case_sensitive``: If False, ignore case in string matching
* ``operator``: Operator to combine multiple feature patterns ("and" or "or")

**Filtering Level Compatibility:**

.. list-table::
   :header-rows: 1

   * - Level
     - Support
     - Behavior
   * - Entity
     - Yes
     - Filters entities that are part of matching patterns
   * - Sequence
     - Yes
     - Keeps sequences containing the pattern
   * - Trajectory
     - Partial
     - Not directly supported. However, sequence-level filters can be propagated 
       to trajectory level when applied with ``intersection=True``, keeping 
       trajectories that contain a matching sequence

**Examples:**

.. code-block:: python

    # Single value pattern
    criterion = PatternCriterion(
        pattern={"health_state": "TREATMENT"},
        contains=True
    )
    
    # Sequential pattern (ordered)
    criterion = PatternCriterion(
        pattern={"health_state": ["SICK", "TREATMENT", "RECOVERY"]},
        contains=True 
    )
    
    # Exact sequence match
    criterion = PatternCriterion(
        pattern={"status": ["A", "B", "C"], "status": ["Z", "Y", "X"]},
        contains=True,
        operator="or" # keep sequence matching one of the patterns
    )
    
    # Regex pattern
    criterion = PatternCriterion(
        pattern={"visit_type": ["regex:^S", "LABORATORY"]},
        contains=True
    )
    
    # Pattern from start
    criterion = PatternCriterion(
        pattern={"event": ["START", "PROCESS"]},
        contains=False  # exclude sequences matching this pattern
    )

**Use cases:**

* Disease progression patterns (e.g., healthy → sick → treatment)
* Care pathway identification
* Sequential event detection
* Regex-based text pattern matching

TimeCriterion
-------------

Time window filtering on temporal boundaries.

**Signature:**

.. code-block:: python

    from tanat.criterion import TimeCriterion
    from datetime import datetime
    
    TimeCriterion(
        start_after: datetime | int | None = None,
        end_before: datetime | int | None = None,
        duration_within: bool = False,
        sequence_within: bool = False
    )

**Parameters:**

* ``start_after``: Minimum start time (datetime for datetime temporal, int for timestep)
* ``start_before``: Maximum start time
* ``end_before``: Maximum end time
* ``end_after``: Minimum end time
* ``duration_within``: If True, entity must be entirely within bounds (only for State/Interval)
* ``sequence_within``: If True, entire sequence temporal extent must be within bounds

**Filtering Level Compatibility:**

.. list-table::
   :header-rows: 1

   * - Level
     - Support
     - Behavior
   * - Entity
     - Yes
     - Filters entities within time window
   * - Sequence
     - Yes
     - Keeps sequences with entities in time window (or entire sequence if ``sequence_within=True``)
    - Trajectory
     - Partial
     - Not directly supported. However, sequence-level filters can be propagated 
       to trajectory level when applied with ``intersection=True``, keeping 
       trajectories that contain a matching sequence

**Examples:**

.. code-block:: python

    from datetime import datetime, timedelta
    
    # Recent time window (last 3 months)
    recent_start = datetime.now() - timedelta(days=90)
    criterion = TimeCriterion(
        start_after=recent_start,
        end_before=datetime.now()
    )
    
    # Entity must be entirely within window
    criterion = TimeCriterion(
        start_after=recent_start,
        end_before=datetime.now(),
        duration_within=True
    )
    
    # Entire sequence must be within window
    criterion = TimeCriterion(
        start_after=datetime(2024, 1, 1),
        end_before=datetime(2024, 12, 31),
        sequence_within=True
    )
    
    # Timestep filtering
    criterion = TimeCriterion(
        start_after=0,
        end_before=100
    )
    
    # Open-ended window
    criterion = TimeCriterion(start_after=datetime(2024, 1, 1))

**Use cases:**

* Time-bounded analysis windows
* Recent data extraction
* Historical period selection
* Study enrollment windows

LengthCriterion
---------------

Sequence length filtering based on entity count.

**Signature:**

.. code-block:: python

    from tanat.criterion import LengthCriterion
    
    LengthCriterion(
        eq: int | None = None,
        ne: int | None = None,
        gt: int | None = None,
        ge: int | None = None,
        lt: int | None = None,
        le: int | None = None
    )

**Parameters:**

* ``eq``: Equal to length
* ``ne``: Not equal to length
* ``gt``: Greater than length
* ``ge``: Greater than or equal to length
* ``lt``: Less than length
* ``le``: Less than or equal to length

**Filtering Level Compatibility:**

.. list-table::
   :header-rows: 1

   * - Level
     - Support
     - Behavior
   * - Entity
     - No
     - Not applicable (entity count is sequence-level property)
   * - Sequence
     - Yes
     - Keeps sequences matching length criteria
   * - Trajectory
     - Partial
     - Not directly supported. However, sequence-level filters can be propagated 
       to trajectory level when applied with ``intersection=True``, keeping 
       trajectories that contain a matching sequence

**Examples:**

.. code-block:: python

    # Sequences with more than 8 entities
    criterion = LengthCriterion(gt=8)
    
    # Sequences with 5 or fewer entities
    criterion = LengthCriterion(le=5)
    
    # Sequences with exactly 10 entities
    criterion = LengthCriterion(eq=10)
    
    # Sequences with at least 3 entities
    criterion = LengthCriterion(ge=3)
    
    # Exclude single-entity sequences
    criterion = LengthCriterion(ne=1)
    
    # Combine with range
    # (use multiple criteria in practice)
    long_sequences = LengthCriterion(ge=5)
    short_sequences = LengthCriterion(le=20)

**Use cases:**

* Minimum data quality requirements (e.g., at least 5 observations)
* Outlier sequence detection
* Sample size validation
* Data sufficiency checks

StaticCriterion
---------------

Filtering based on static (non-temporal) features.

**Signature:**

.. code-block:: python

    from tanat.criterion import StaticCriterion
    
    StaticCriterion(query: str)

**Parameters:**

* ``query``: Pandas query expression on static data (same syntax as QueryCriterion)

**Filtering Level Compatibility:**

.. list-table::
   :header-rows: 1

   * - Level
     - Support
     - Behavior
   * - Entity
     - No
     - Not applicable (static features are at sequence/trajectory level)
   * - Sequence
     - Yes
     - Keeps sequences with matching static features
   * - Trajectory
     - Yes
     - Keeps trajectories with matching static features

**Examples:**

.. code-block:: python

    # Demographic filtering
    criterion = StaticCriterion(query="age > 65")
    
    # Multiple static conditions
    criterion = StaticCriterion(
        query="age > 65 and chronic_condition == True"
    )
    
    # Categorical filtering
    criterion = StaticCriterion(query="gender == 'F'")
    
    # Risk stratification
    criterion = StaticCriterion(query="risk_level == 'HIGH'")
    
    # Insurance type
    criterion = StaticCriterion(
        query="insurance in ['PUBLIC', 'MIXED']"
    )
    
    # Comorbidity threshold
    criterion = StaticCriterion(query="comorbidity_count >= 3")

**Use cases:**

* Demographic cohort selection (age, gender, etc.)
* Clinical characteristic filtering (risk level, conditions)
* Subgroup analysis
* Stratified sampling

Applying Criterion
==================

All criterion use the ``filter()`` method on pools.

Basic Filtering
---------------

.. code-block:: python

    # Entity-level filtering
    filtered_pool = pool.filter(criterion, level="entity")
    
    # Sequence-level filtering
    filtered_pool = pool.filter(criterion, level="sequence")
    
    # Default level (typically sequence)
    filtered_pool = pool.filter(criterion)

Identifying Matches
-------------------

Use ``which()`` to get IDs of matching sequences without filtering.

.. code-block:: python

    # Get sequence IDs matching criterion
    matching_ids = pool.which(criterion)
    
    # Type: set of sequence IDs
    print(type(matching_ids))  # <class 'set'>
    
    # Use for set operations
    cohort_a = pool.which(criterion_a)
    cohort_b = pool.which(criterion_b)
    intersection = cohort_a.intersection(cohort_b)

Advanced Filtering
==================

Combining Multiple Criterion
-----------------------------

Use sequential filtering or set operations.

**Sequential approach:**

.. code-block:: python

    # Apply filters in sequence
    pool_filtered = (
        pool
        .filter(StaticCriterion(query="age > 65"))
        .filter(QueryCriterion(query="visit_type == 'EMERGENCY'"), level="sequence")
        .filter(LengthCriterion(gt=5))
    )

**Set-based approach:**

.. code-block:: python

    # Get IDs for each criterion
    elderly = pool.which(StaticCriterion(query="age > 65"))
    with_emergency = pool.which(
        QueryCriterion(query="visit_type == 'EMERGENCY'")
    )
    sufficient_data = pool.which(LengthCriterion(gt=5))
    
    # Combine with set operations
    final_cohort = elderly.intersection(with_emergency).intersection(sufficient_data)
    
    # Create filtered pool
    filtered_pool = pool.subset(final_cohort)

Negation and Exclusion
-----------------------

Exclude sequences matching a criterion.

.. code-block:: python

    # Get all sequence IDs
    all_ids = set(pool.unique_ids)
    
    # Get IDs to exclude
    to_exclude = pool.which(criterion)
    
    # Get complement
    to_keep = all_ids - to_exclude
    
    # Create filtered pool
    filtered_pool = pool.subset(to_keep)

Conditional Filtering
---------------------

Apply different criterion based on conditions.

.. code-block:: python

    # Different criteria for different risk levels
    high_risk_pool = pool.filter(StaticCriterion(query="risk_level == 'HIGH'"))
    low_risk_pool = pool.filter(StaticCriterion(query="risk_level == 'LOW'"))
    
    # Apply risk-specific criteria
    high_risk_filtered = high_risk_pool.filter(LengthCriterion(gt=10))
    low_risk_filtered = low_risk_pool.filter(LengthCriterion(gt=5))

API Reference
=============

For complete API documentation, see:

* :py:class:`tanat.criterion.QueryCriterion` - Query-based filtering
* :py:class:`tanat.criterion.PatternCriterion` - Pattern matching
* :py:class:`tanat.criterion.TimeCriterion` - Time window filtering
* :py:class:`tanat.criterion.LengthCriterion` - Length-based filtering
* :py:class:`tanat.criterion.StaticCriterion` - Static feature filtering

See Also
========

* :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_sequence` - Hands-on filtering examples
* :doc:`/getting-started/concepts` - Conceptual overview of filtering
* :doc:`alignment` - Temporal alignment after filtering
* :doc:`metadata` - Understanding feature types for queries
* :doc:`manipulation` -  Data manipulation methods 