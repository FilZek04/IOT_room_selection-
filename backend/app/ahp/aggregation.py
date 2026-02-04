"""Score aggregation for AHP algorithm."""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class AggregationMethod(Enum):
    WEIGHTED_SUM = "weighted_sum"
    WEIGHTED_PRODUCT = "weighted_product"
    COMBINED = "combined"


@dataclass
class CriterionScore:
    criterion_id: str
    criterion_name: str
    raw_value: float
    normalized_score: float
    weight: float


@dataclass  
class RoomScore:
    room_id: str
    room_name: str
    final_score: float
    rank: int = 0
    criterion_scores: List[CriterionScore] = field(default_factory=list)
    comfort_score: float = 0.0
    health_score: float = 0.0
    usability_score: float = 0.0


def aggregate_weighted_sum(
    scores: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """Calculate weighted sum: S = sum(w_i * s_i)."""
    if not scores or not weights:
        return 0.0
    
    total = 0.0
    weight_sum = 0.0
    
    for criterion_id, score in scores.items():
        weight = weights.get(criterion_id, 0.0)
        total += weight * score
        weight_sum += weight
    
    if weight_sum > 0 and not np.isclose(weight_sum, 1.0):
        total /= weight_sum
    
    return total


def aggregate_weighted_product(
    scores: Dict[str, float],
    weights: Dict[str, float],
    epsilon: float = 0.001
) -> float:
    """Calculate weighted product: S = product(s_i ^ w_i)."""
    if not scores or not weights:
        return 0.0
    
    product = 1.0
    weight_sum = 0.0
    
    for criterion_id, score in scores.items():
        weight = weights.get(criterion_id, 0.0)
        if weight == 0:
            continue
        safe_score = max(epsilon, score)
        product *= safe_score ** weight
        weight_sum += weight
    
    if weight_sum > 0 and not np.isclose(weight_sum, 1.0):
        product = product ** (1.0 / weight_sum)
    
    return product


def aggregate_combined(
    scores: Dict[str, float],
    weights: Dict[str, float],
    wsm_weight: float = 0.7
) -> float:
    """Combined aggregation using both WSM (70%) and WPM (30%)."""
    wsm_score = aggregate_weighted_sum(scores, weights)
    wpm_score = aggregate_weighted_product(scores, weights)
    
    return wsm_weight * wsm_score + (1 - wsm_weight) * wpm_score


def aggregate_with_hierarchy(
    leaf_scores: Dict[str, float],
    hierarchy_weights: Dict[str, Dict[str, float]],
    method: AggregationMethod = AggregationMethod.WEIGHTED_SUM
) -> Tuple[float, Dict[str, float]]:
    """Aggregate scores respecting AHP hierarchy structure."""
    aggregator = _get_aggregator(method)
    
    main_criteria_scores = {}
    
    for main_criterion in ["Comfort", "Health", "Usability"]:
        if main_criterion not in hierarchy_weights:
            continue
        
        sub_weights = hierarchy_weights[main_criterion]
        sub_scores = {k: leaf_scores.get(k, 0.0) for k in sub_weights.keys()}
        
        main_criteria_scores[main_criterion] = aggregator(sub_scores, sub_weights)
    
    main_weights = hierarchy_weights.get("main", {})
    final_score = aggregator(main_criteria_scores, main_weights)
    
    return final_score, main_criteria_scores


def rank_rooms(room_scores: List[RoomScore]) -> List[RoomScore]:
    """Sort rooms by score and assign ranks."""
    sorted_rooms = sorted(room_scores, key=lambda r: r.final_score, reverse=True)
    
    current_rank = 1
    for i, room in enumerate(sorted_rooms):
        if i > 0 and not np.isclose(room.final_score, sorted_rooms[i-1].final_score):
            current_rank = i + 1
        room.rank = current_rank
    
    return sorted_rooms


def format_ranking(room_scores: List[RoomScore], detailed: bool = False) -> str:
    """Format room rankings as readable string."""
    lines = ["=" * 50, "ROOM RANKING RESULTS", "=" * 50, ""]
    
    for room in room_scores:
        lines.append(f"Rank {room.rank}: {room.room_name}")
        lines.append(f"   Final Score: {room.final_score:.4f} ({room.final_score*100:.1f}%)")
        
        if detailed or room.rank <= 3:
            lines.append(f"   Comfort:   {room.comfort_score:.3f}")
            lines.append(f"   Health:    {room.health_score:.3f}")
            lines.append(f"   Usability: {room.usability_score:.3f}")
        
        lines.append("")
    
    return "\n".join(lines)


def _get_aggregator(method: AggregationMethod):
    """Get aggregation function for specified method."""
    if method == AggregationMethod.WEIGHTED_SUM:
        return aggregate_weighted_sum
    elif method == AggregationMethod.WEIGHTED_PRODUCT:
        return aggregate_weighted_product
    elif method == AggregationMethod.COMBINED:
        return aggregate_combined
    else:
        raise ValueError(f"Unknown aggregation method: {method}")
