#!/usr/bin/env python3
"""
Test rank criterion applied to individual sequences.
"""

import pytest

from tanat.criterion.entity.type.rank.settings import RankCriterion


class TestRankCriterionSequence:
    """
    Test rank criterion applied to individual sequences.
    """

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_first_entity_on_sequence(self, sequence_pools, pool_type, snapshot):
        """
        Test filtering to keep only the first entity on an individual sequence (inplace=False).
        """
        pool = sequence_pools[pool_type]

        # Get first sequence
        seq_id = list(pool.unique_ids)[0]
        sequence = pool.get_sequences()[seq_id]
        original_data = sequence.sequence_data.copy()

        # Keep only the first entity
        rank_criterion = RankCriterion(first=1)

        # Filter
        filtered_sequence = sequence.filter(rank_criterion, inplace=False)

        # Check original data is unchanged
        assert sequence.sequence_data.equals(original_data)
        assert filtered_sequence is not sequence
        snapshot.assert_match(filtered_sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_first_entity_on_sequence_inplace(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test filtering to keep only the first entity on an individual sequence (inplace=True).
        """
        pool = sequence_pools[pool_type]

        # Get first sequence and copy it
        seq_id = list(pool.unique_ids)[0]
        sequence = pool.get_sequences()[seq_id].copy()

        # Keep only the first entity
        rank_criterion = RankCriterion(first=1)

        # Filter inplace
        result = sequence.filter(rank_criterion, inplace=True)

        assert result is None
        snapshot.assert_match(sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_last_entity_on_sequence(self, sequence_pools, pool_type, snapshot):
        """
        Test filtering to keep only the last entity on an individual sequence (inplace=False).
        """
        pool = sequence_pools[pool_type]

        # Get first sequence
        seq_id = list(pool.unique_ids)[0]
        sequence = pool.get_sequences()[seq_id]
        original_data = sequence.sequence_data.copy()

        # Keep only the last entity
        rank_criterion = RankCriterion(last=1)

        # Filter
        filtered_sequence = sequence.filter(rank_criterion, inplace=False)

        # Check original data is unchanged
        assert sequence.sequence_data.equals(original_data)
        assert filtered_sequence is not sequence
        snapshot.assert_match(filtered_sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_relative_ranks_on_sequence(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test filtering with relative ranks around T0 on an individual sequence (inplace=False).
        """
        pool = sequence_pools[pool_type]

        # Get first sequence
        seq_id = list(pool.unique_ids)[0]
        sequence = pool.get_sequences()[seq_id]
        original_data = sequence.sequence_data.copy()

        # Keep entities at relative ranks -1, 0, 1
        rank_criterion = RankCriterion(ranks=[-1, 0, 1], relative=True)

        # Filter
        filtered_sequence = sequence.filter(rank_criterion, inplace=False)

        # Check original data is unchanged
        assert sequence.sequence_data.equals(original_data)
        assert filtered_sequence is not sequence

        snapshot.assert_match(filtered_sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_absolute_ranks_on_sequence(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test filtering with absolute ranks on an individual sequence (inplace=False).
        """
        pool = sequence_pools[pool_type]

        # Get first sequence
        seq_id = list(pool.unique_ids)[0]
        sequence = pool.get_sequences()[seq_id]
        original_data = sequence.sequence_data.copy()

        # Keep positions 0 and 1
        rank_criterion = RankCriterion(ranks=[0, 1], relative=False)

        # Filter
        filtered_sequence = sequence.filter(rank_criterion, inplace=False)

        # Check original data is unchanged
        assert sequence.sequence_data.equals(original_data)
        assert filtered_sequence is not sequence
        snapshot.assert_match(filtered_sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_out_of_bound_on_sequence(self, pool_type, sequence_pools, snapshot):
        """
        Test filtering with out-of-bound ranks on a single sequence.

        When all entities are filtered out (ranks beyond sequence length),
        the filtered sequence should return an empty DataFrame instead of raising an error.
        This behavior is consistent with pool-level filtering.
        """
        pool = sequence_pools[pool_type]
        sequence_id = list(pool.unique_ids)[0]
        sequence = pool[sequence_id]

        # Filter with ranks that are all out of bounds
        rank_criterion = RankCriterion(ranks=[100, 200, 300])
        filtered_sequence = sequence.filter(rank_criterion, inplace=False)

        # Verify with snapshot
        snapshot.assert_match(filtered_sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_consistency_on_sequence(self, sequence_pools, pool_type):
        """
        Check filter with inplace=True and inplace=False produce the same results on a sequence.
        """
        pool = sequence_pools[pool_type]

        # Get first sequence
        seq_id = list(pool.unique_ids)[0]
        original_sequence = pool.get_sequences()[seq_id]
        rank_criterion = RankCriterion(first=2)

        # Non inplace
        filtered_sequence_non_inplace = original_sequence.filter(
            rank_criterion, inplace=False
        )
        non_inplace_result = filtered_sequence_non_inplace.sequence_data

        # Inplace
        sequence_copy = original_sequence.copy()
        sequence_copy.filter(rank_criterion, inplace=True)
        inplace_result = sequence_copy.sequence_data

        # Test
        assert non_inplace_result.equals(inplace_result)

    def test_filter_entities_on_state_sequence_raises_not_implemented_error(
        self, sequence_pools
    ):
        """
        Filter entities should raise a NotImplementedError.
        """
        state_pool = sequence_pools["state"]
        sequence = state_pool[1]
        rank_criterion = RankCriterion(first=1)

        with pytest.raises(NotImplementedError):
            sequence.filter(rank_criterion)
