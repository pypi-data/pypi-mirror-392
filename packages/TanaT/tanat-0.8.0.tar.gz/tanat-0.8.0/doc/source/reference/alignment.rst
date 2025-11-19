.. _alignment_reference:

===================
Temporal Alignment
===================

Reference documentation for TanaT's temporal alignment system (T0 management and transformations).

Overview
========

Temporal alignment enables synchronization of sequences by defining a common reference point (T0) for each sequence.
This is essential for:

* Comparative cohort analysis
* Event-aligned studies (e.g., all patients aligned to first hospitalization)
* Longitudinal pattern detection
* Time-to-event analysis

All sequences start with **absolute time** (datetime or timestep). After setting T0, you can transform to **relative time** or **relative rank**.

Setting Reference Dates (T0)
=============================

TanaT provides multiple methods to set reference dates based on different alignment strategies.

zero_from_position()
--------------------

Set T0 based on entity position within each sequence.

.. Note::
    This is the default alignment method when no other zeroing is applied (position = 0).

**Signature:**

.. code-block:: python

    pool.zero_from_position(position: int = 0) -> self

**Parameters:**

* ``position``: Zero-indexed position (default: 0 = first entity)

**Examples:**

.. code-block:: python

    # Align to first entity (default behavior)
    pool.zero_from_position(position=0)
    
    # Align to third entity
    pool.zero_from_position(position=2)
    
    # Align to last entity (use negative indexing)
    pool.zero_from_position(position=-1)

**Use cases:**

* First entity alignment: All sequences start at T0 = 0
* Fixed position analysis: Compare sequences from Nth event
* Last entity alignment: Retrospective analysis from final event

Direct T0 Assignment
--------------------

Manually set reference dates using the ``t_zero`` property.

**Signature:**

.. code-block:: python

    pool.t_zero = {sequence_id: datetime, ...}

**Example:**

.. code-block:: python

    from datetime import datetime
    
    # Set custom T0 for specific sequences
    pool.t_zero = {
        "patient_001": datetime(2024, 1, 15),
        "patient_002": datetime(2024, 2, 10),
        "patient_003": datetime(2024, 1, 20)
    }

**Use cases:**

* External reference dates (e.g., birth date, diagnosis date from another dataset)
* Study enrollment dates
* Custom milestone dates

zero_from_query()
-----------------

Set T0 based on the occurrence of specific entities matching a query.

**Signature:**

.. code-block:: python

    pool.zero_from_query(
        query: str,
        use_first: bool = True,
        anchor: str = "start/middle/end",
    ) -> self

**Parameters:**

* ``query``: Pandas-style query string to identify reference entities
* ``use_first``: If True, use first matching entity (default: True). If False, use last matching entity.
* ``anchor``: Reference point within periods for time calculation. Options: "start", "middle", "end".

**Examples:**

.. code-block:: python

    # Align to first emergency visit
    pool.zero_from_query(
        query="visit_type == 'EMERGENCY'",
        use_first=True
    )
    
    # Align to last treatment event
    pool.zero_from_query(
        query="status == 'TREATMENT'",
        use_last=True
    )
    
    # Complex query with multiple conditions
    pool.zero_from_query(
        query="age > 65 and diagnosis == 'DIABETES'"
    )

**Behavior:**

* Sequences without matching entities will have ``None`` as T0
* Use ``drop_na=True`` in transformation methods to exclude these sequences

Temporal Transformations
========================

After setting T0, transform absolute time to relative representations.

to_relative_time()
------------------

Convert timestamps to relative time from T0.

**Signature:**

.. code-block:: python

    pool.to_relative_time(
        granularity: str = "day",
        drop_na: bool = False
    ) -> self

**Parameters:**

* ``granularity``: Time unit for relative time

  * Datetime temporal: ``"year"``, ``"month"``, ``"week"``, ``"day"``, ``"hour"``, ``"minute"``, ``"second"``
  * Timestep temporal: ``"unit"`` (raw timestep difference)

* ``drop_na``: If True, remove entities without valid T0

**Examples:**

.. code-block:: python

    # Convert to days from T0
    pool.to_relative_time(granularity="day")
    
    # Convert to hours, excluding sequences without T0
    pool.to_relative_time(
        granularity="hour",
        drop_na=True
    )
    
    # For timestep data
    timestep_pool.to_relative_time(granularity="unit")

**Resulting time values:**

* Negative values: Events before T0
* Zero: Events at T0
* Positive values: Events after T0

to_relative_rank()
------------------

Convert to ordinal positions relative to T0.

**Signature:**

.. code-block:: python

    pool.to_relative_rank(drop_na: bool = False) -> self

**Parameters:**

* ``drop_na``: If True, remove entities without valid T0

**Examples:**

.. code-block:: python

    # Convert to relative ranks
    pool.to_relative_rank()
    
    # With missing T0 handling
    pool.to_relative_rank(drop_na=True)

**Resulting rank values:**

* Negative ranks: Entities before T0 (-1 = immediately before)
* Zero: Entity at T0
* Positive ranks: Entities after T0 (+1 = immediately after)

**Use cases:**

* Sequential pattern analysis regardless of time intervals
* Comparing sequences with different temporal scales
* Order-based analysis (1st event after T0, 2nd event after T0, etc.)

Workflow Examples
=================

Complete Alignment Workflow
----------------------------

Typical workflow for temporal alignment and analysis.

.. code-block:: python

    # 1. Set reference dates
    pool.zero_from_query(
        query="visit_type == 'EMERGENCY'",
        use_first=True
    )
    
    # 2. Transform to relative time
    pool.to_relative_time(
        granularity="day",
        drop_na=True  # Exclude sequences without emergency visits
    )
    
    # 3. Filter time window around T0
    from tanat.criterion import TimeCriterion
    
    analysis_window = TimeCriterion(
        start_after=-30,  # 30 days before T0
        end_before=90      # 90 days after T0
    )
    
    aligned_pool = pool.filter(analysis_window, level="entity")
    
    # 4. Visualize aligned sequences
    from tanat.visualization.sequence import SequenceVisualizer
    
    SequenceVisualizer.timeline(
        relative_time=True, # will use T0 prior defined
        granularity="day"
    ).draw(aligned_pool)


Accessing T0 Information
========================

Inspect reference dates.

**Check T0 values:**

.. code-block:: python

    # View T0 dictionary
    print(pool.t_zero)
    # Output: {'seq-001': Timestamp(...), 'seq-002': None, ...}

**Convert to DataFrame:**

.. code-block:: python

    import pandas as pd
    
    t0_df = pd.DataFrame.from_dict(
        pool.t_zero,
        orient="index",
        columns=["T0"]
    )
    t0_df.describe()

Zeroing Configuration
=====================

Advanced configuration using the ``zeroing`` module (typically for internal use or custom implementations).

Available Zeroing Strategies
-----------------------------

The ``tanat.zeroing`` module provides three main strategies:

* **QueryZeroingSetter**: Entity query-based (used by ``zero_from_query()``)
* **PositionZeroingSetter**: Position-based (used by ``zero_from_position()``)
* **DirectZeroingSetter**: Manual assignment (used by ``t_zero`` property)

For most use cases, use the pool methods directly rather than instantiating setters manually.

API Reference
=============

For complete API documentation, see:

* :py:class:`tanat.sequence.EventSequencePool` - Sequence pool methods
* :py:class:`tanat.trajectory.TrajectoryPool` - Trajectory pool methods
* :py:mod:`tanat.zeroing` - Zeroing module (advanced usage)

See Also
========

* :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_sequence` - Hands-on alignment examples
* :doc:`/getting-started/concepts` - Conceptual overview of temporal alignment
* :doc:`criterion` - Filtering aligned sequences
* :doc:`metadata` - Temporal metadata configuration
