#!/usr/bin/env python3
"""
Settings for rank-based filtering.
"""

from typing import Optional, Union
from pydantic import Field, field_validator, model_validator
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ....base.settings import Criterion
from ....decorator.entity import entity_compatible


@viewer
@entity_compatible
@dataclass
class RankCriterion(Criterion):
    """
    Filter entities by their rank (ordinal position) in the sequence.

    Supports both relative and absolute filtering modes.
    Only applicable at entity level.

    In relative mode (relative=True), ranks are computed relative to the
    reference date (T0). Negative ranks reference entities occurring before T0,
    and positive ranks reference entities after T0.

    In absolute mode (relative=False, default), ranks are 0-indexed positions
    in the sequence, where 0 is the first entity regardless of temporal position.

    Args:
        first (int, optional):
            Keep first n entities per sequence.
            - If n > 0: Keep first n entities (like [:n] in Python)
            - If n < 0: Keep all EXCEPT last |n| entities (like [:-n] in Python)
            - n cannot be 0
            Examples: first=3 → [0,1,2], first=-2 → all except last 2
        last (int, optional):
            Keep last n entities per sequence.
            - If n > 0: Keep last n entities (like [-n:] in Python)
            - If n < 0: Keep all EXCEPT first |n| entities (like [n:] in Python)
            - n cannot be 0
            Examples: last=2 → last 2 entities, last=-3 → all except first 3
        start (int, optional):
            Start rank (inclusive, 0-indexed).
            - If relative=False: Python-style indexing (negative = from end)
              Example: start=0 (first), start=-5 (5th from end)
            - If relative=True: Temporal rank relative to T0 (negative = before T0)
              Example: start=-10 (rank -10 before T0)
        end (int, optional):
            End rank (exclusive, 0-indexed).
            - If relative=False: Python-style indexing (negative = from end)
              Example: end=10, end=-2 (excludes last 2)
            - If relative=True: Temporal rank relative to T0 (negative = before T0)
              Example: end=50 (up to rank 50 after T0)
        step (int, optional):
            Step size for sampling within range. Default: None (equivalent to 1).
            - Must be >= 1 (positive only for temporal sequences)
            - step=1: Keep all elements (default behavior)
            - step=2: Every 2nd element (sub-sampling)
            - step=10: Every 10th element (sparse sampling)
            - Works in both absolute and relative modes
            Examples:
              - step=2 → [0, 2, 4, 6, ...] (every 2nd element)
              - step=10 → [0, 10, 20, ...] (every 10th element)
        ranks (list[int], optional):
            Specific ranks to keep (0-indexed positions).
            - If relative=False: Python-style indexing (negative = from end)
              Example: ranks=[0, -1] (first and last)
            - If relative=True: Temporal ranks relative to T0 (negative = before T0)
              Example: ranks=[-5, 0, 5] (ranks around T0)
        relative (bool):
            Filtering mode. Default: False.
            - False: Absolute mode - Python-style indexing (negative = from end)
            - True: Relative mode - temporal ranks relative to T0 (negative = before T0)

    Examples:
        >>> # Keep first 40 entities (absolute positions)
        >>> criterion = RankCriterion(first=40)
        >>> filtered_pool = pool.filter(criterion, level="entity")

        >>> # Keep all except last 5 entities
        >>> criterion = RankCriterion(first=-5)

        >>> # Keep last 20 entities
        >>> criterion = RankCriterion(last=20)

        >>> # Keep all except first 10 entities
        >>> criterion = RankCriterion(last=-10)

        >>> # Keep positions 10-50 (absolute mode, Python-style)
        >>> criterion = RankCriterion(start=10, end=50)

        >>> # Keep from index 5 until 2nd from end
        >>> criterion = RankCriterion(start=5, end=-2)

        >>> # Keep last 10 positions
        >>> criterion = RankCriterion(start=-10)

        >>> # Sub-sample every 10th entity (absolute mode)
        >>> criterion = RankCriterion(start=0, end=100, step=10)

        >>> # Keep ranks -10 to 50 relative to T0, every 5 ranks (temporal)
        >>> criterion = RankCriterion(start=-10, end=50, step=5, relative=True)

        >>> # Sample first, last, and middle
        >>> criterion = RankCriterion(ranks=[0, 5, -3, -1])

        >>> # Sample around T0 (relative mode, temporal)
        >>> criterion = RankCriterion(ranks=[-5, -2, 0, 2, 5, 10], relative=True)

    Note:
        - Only ONE parameter group should be specified:
          (first) OR (last) OR (start/end/step) OR (ranks)
        - step is only compatible with start/end parameters
        - step must be >= 1 (no backward/reversal for temporal sequences)
        - Permissive slicing: Invalid slices (e.g., start > end with step > 0)
          return empty sequences without error (Python behavior)
        - In relative=True mode: negative values indicate temporal position before T0
        - In relative=False mode: negative values use Python indexing (from end)
        - Not supported for StateSequence (breaks temporal continuity)
    """

    first: Optional[int] = Field(default=None)
    last: Optional[int] = Field(default=None)
    start: Optional[int] = None
    end: Optional[int] = None
    step: Optional[int] = Field(default=None, ge=1)
    ranks: Optional[Union[list[int]]] = None
    relative: bool = False

    _REGISTER_NAME = "rank"

    @field_validator("ranks")
    @classmethod
    def validate_ranks(cls, v):
        """Convert unique int to list."""
        if v is None:
            return None

        # Convert unique value to list
        return list(v) if isinstance(v, int) else v

    @model_validator(mode="after")
    def validate_exclusivity(self):
        """Ensure only one parameter group is specified."""
        param_groups = [
            self.first is not None,
            self.last is not None,
            (self.start is not None)
            or (self.end is not None)
            or (self.step is not None),
            self.ranks is not None,
        ]

        if sum(param_groups) == 0:
            raise ValueError(
                "At least one parameter must be specified: "
                "(first) OR (last) OR (start/end/step) OR (ranks)"
            )

        if sum(param_groups) > 1:
            raise ValueError(
                "Only one parameter group allowed: "
                "(first) OR (last) OR (start/end/step) OR (ranks)"
            )

        return self

    @model_validator(mode="after")
    def validate_step_compatibility(self):
        """Ensure step is only used with start/end."""
        if self.step is not None:
            if self.first is not None or self.last is not None:
                raise ValueError(
                    "step is incompatible with first/last parameters. "
                    "Use start/end instead."
                )
            if self.ranks is not None:
                raise ValueError(
                    "step is incompatible with ranks parameter. "
                    "Use start/end instead."
                )
        return self

    @model_validator(mode="after")
    def validate_non_zero(self):
        """Ensure first and last are not zero."""
        if self.first == 0:
            raise ValueError(
                "first cannot be 0. Use positive for first n, negative for all except last |n|."
            )

        if self.last == 0:
            raise ValueError(
                "last cannot be 0. Use positive for last n, negative for all except first |n|."
            )

        return self
