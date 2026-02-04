"""
AHP (Analytic Hierarchy Process) Algorithm Package.

This package provides a complete implementation of the AHP algorithm
for multi-criteria room selection.

Main components:
- pairwise_matrix: Saaty pairwise comparison matrices
- eigenvector: Priority weight and consistency calculation
- score_mapping: Sensor data to score mapping functions
- aggregation: Weighted score aggregation methods
- ahp_engine: Main orchestrator class
"""

from .pairwise_matrix import PairwiseMatrix
from .eigenvector import (
    calculate_priority_weights,
    calculate_consistency_ratio,
    validate_matrix_consistency,
)
from .score_mapping import (
    map_temperature, map_co2, map_humidity,
    map_light, map_noise, map_voc, map_air_quality,
)
from .aggregation import RoomScore, AggregationMethod, rank_rooms
from .ahp_engine import AHPEngine, RoomData, UserRequirements, AHPResult

__all__ = [
    "PairwiseMatrix",
    "calculate_priority_weights",
    "calculate_consistency_ratio",
    "validate_matrix_consistency",
    "map_temperature", "map_co2", "map_humidity",
    "map_light", "map_noise", "map_voc", "map_air_quality",
    "RoomScore", "AggregationMethod", "rank_rooms",
    "AHPEngine", "RoomData", "UserRequirements", "AHPResult",
]