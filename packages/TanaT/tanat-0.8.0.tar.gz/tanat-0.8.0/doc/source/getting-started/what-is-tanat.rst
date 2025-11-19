What is TanaT?
==============

*TanaT* (*Temporal ANalysis of Trajectories*) is an extensible Python library for temporal sequence analysis with a primary focus on patient care pathways.

The name also refers to a variety of wine grape that originates from south of France, taking continuity with the `TraMineR library <http://traminer.unige.ch/>`_ which widely inspired this work (Traminer is also a variety of wine grape).

Key Features
------------

**Expressive Data Representation**
    TanaT provides a very expressive and flexible representation of event-based temporal data, distinguishing between entities, sequences, and trajectories.

**Multiple Sequence Types**
    Support for event sequences (point-in-time), interval sequences (duration-based), and state sequences (continuous states).

**Advanced Analytics**
    Implements different metrics and clustering algorithms specifically designed for temporal sequence data.

**Extensible Architecture**
    Built with extensibility in mind, making it easy to add new metrics, clustering methods, and analysis techniques.

What Makes TanaT Different?
---------------------------

Unlike traditional time series libraries, TanaT is designed for **irregularly sampled, symbolic event-based temporal data**. 
We classify timed sequences data as *non-euclidean* in the sense that there is no natural euclidean space to represent collections of timed sequences.

For instance:

* Timed sequences in a pool don't necessarily have the same length (same number of events)
* Events themselves have no natural euclidean representation (when using symbolic event types)
* Traditional data analysis methods don't apply directly to these *non-euclidean* data

Core framework functionalities
------------------------------

The TanaT framework provides a complete workflow for temporal sequence analysis, from data ingestion to advanced analytics and visualization.

.. image:: ../static/tanat_ecosystem.png
   :align: center
   :alt: TanaT Framework Overview

**Simulation**
   Synthetic data generation for statistical power analysis and comprehensive benchmarking of algorithms

**Visualization**
   Rich visualization tools for exploring and interpreting temporal sequences and analysis results

**Data Wrangling**
   Flexible data manipulation, filtering, and transformation capabilities

**Survival Analysis**
   Integration with survival analysis techniques for time-to-event data

**Metrics & Clustering**
   Distance metrics and clustering algorithms specifically designed for temporal sequences

**Workflow Orchestration**
   Pipeline management for reproducible and automated analysis workflows

Inspiration and Related Work
----------------------------

TanaT has been strongly inspired by:

* The `TraMineR <http://traminer.unige.ch/>`_ library for the analysis of state sequences in R
* Libraries dedicated to time series analysis such as `aeon <https://www.aeon-toolkit.org/>`_ and `tslearn <https://tslearn.readthedocs.io/>`_

**Core Team:**

- Arnaud Duvermy (design, core architecture, maintenance)  
- Thomas Guyet (project leader, design, development of data analysis methods, documentation)

**Contact:** tanat@inria.fr

This work benefits from the advice of Mike Rye.

Links
-----

* `Homepage <https://tanat.gitlabpages.inria.fr/core/tanat/>`_
* `Source Code <https://gitlab.inria.fr/tanat/core/tanat.git>`_
* `Issues <https://gitlab.inria.fr/tanat/core/tanat/-/issues>`_