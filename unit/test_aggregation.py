"""
Unit tests for aggregation utilities.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.ahp.aggregation import (
    aggregate_weighted_sum,
    aggregate_weighted_product,
    aggregate_combined,
    aggregate_with_hierarchy,
    rank_rooms,
    RoomScore,
    AggregationMethod,
    format_ranking,
    _get_aggregator,
)


class TestWeightedSum:
    """Tests for weighted sum aggregation."""

    def test_normalizes_when_weights_do_not_sum_to_one(self):
        scores = {"a": 0.8, "b": 0.4}
        weights = {"a": 0.8, "b": 0.4}  # sums to 1.2

        result = aggregate_weighted_sum(scores, weights)

        expected = (0.8 * 0.8 + 0.4 * 0.4) / 1.2
        assert pytest.approx(result, rel=1e-6) == expected


class TestWeightedProduct:
    """Tests for weighted product aggregation."""

    def test_uses_epsilon_for_zero_scores(self):
        scores = {"a": 0.0, "b": 1.0}
        weights = {"a": 0.5, "b": 0.5}

        result = aggregate_weighted_product(scores, weights)

        # Expected: sqrt(epsilon) since one score is zero with weight 0.5
        expected = (0.001 ** 0.5) * (1.0 ** 0.5)
        assert pytest.approx(result, rel=1e-6) == expected


class TestCombinedAggregation:
    """Tests for combined aggregation."""

    def test_combined_blends_wsm_and_wpm(self):
        scores = {"a": 1.0, "b": 0.25}
        weights = {"a": 0.6, "b": 0.4}

        wsm = aggregate_weighted_sum(scores, weights)
        wpm = aggregate_weighted_product(scores, weights)

        result = aggregate_combined(scores, weights, wsm_weight=0.25)

        expected = 0.25 * wsm + 0.75 * wpm
        assert pytest.approx(result, rel=1e-6) == expected


class TestHierarchyAggregation:
    """Tests for hierarchical aggregation and ranking."""

    def test_aggregate_with_hierarchy_returns_expected_scores(self):
        leaf_scores = {
            "Temperature": 1.0,
            "Lighting": 0.5,
            "CO2": 0.75,
            "SeatingCapacity": 0.8,
        }
        hierarchy_weights = {
            "main": {"Comfort": 0.4, "Health": 0.35, "Usability": 0.25},
            "Comfort": {"Temperature": 0.6, "Lighting": 0.4},
            "Health": {"CO2": 1.0},
            "Usability": {"SeatingCapacity": 1.0},
        }

        final_score, main_scores = aggregate_with_hierarchy(
            leaf_scores, hierarchy_weights, AggregationMethod.WEIGHTED_SUM
        )

        assert pytest.approx(main_scores["Comfort"], rel=1e-6) == 0.8
        assert pytest.approx(main_scores["Health"], rel=1e-6) == 0.75
        assert pytest.approx(main_scores["Usability"], rel=1e-6) == 0.8

        expected_final = 0.4 * 0.8 + 0.35 * 0.75 + 0.25 * 0.8
        assert pytest.approx(final_score, rel=1e-6) == expected_final

    def test_rank_rooms_handles_ties(self):
        room1 = RoomScore("R1", "Room 1", final_score=0.8)
        room2 = RoomScore("R2", "Room 2", final_score=0.8)
        room3 = RoomScore("R3", "Room 3", final_score=0.6)

        ranked = rank_rooms([room1, room2, room3])

        assert [r.rank for r in ranked] == [1, 1, 3]

    def test_format_ranking_includes_breakdown(self):
        room1 = RoomScore(
            room_id="R1",
            room_name="Room 1",
            final_score=0.9,
            rank=1,
            comfort_score=0.85,
            health_score=0.88,
            usability_score=0.9,
        )
        room2 = RoomScore(
            room_id="R2",
            room_name="Room 2",
            final_score=0.7,
            rank=2,
            comfort_score=0.65,
            health_score=0.7,
            usability_score=0.72,
        )

        text = format_ranking(rank_rooms([room1, room2]), detailed=True)

        assert "ROOM RANKING RESULTS" in text
        assert "Rank 1: Room 1" in text
        assert "Comfort" in text and "Health" in text and "Usability" in text


class TestAggregatorSelection:
    """Tests for aggregator selection helper."""

    def test_invalid_aggregation_method_raises(self):
        with pytest.raises(ValueError):
            _get_aggregator("invalid")
