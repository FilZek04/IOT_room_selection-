"""AHP Engine - Main orchestrator for room selection."""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from .pairwise_matrix import (
    PairwiseMatrix,
    create_default_criteria_matrix,
    create_comfort_subcriteria_matrix,
    create_health_subcriteria_matrix,
    create_usability_subcriteria_matrix,
)
from .eigenvector import (
    calculate_priority_weights,
    calculate_consistency_ratio,
    validate_matrix_consistency,
)
from .score_mapping import (
    map_temperature, map_co2, map_humidity, map_light,
    map_noise, map_voc, map_air_quality,
    map_seating_capacity, map_equipment, map_av_facilities,
)
from .aggregation import (
    aggregate_with_hierarchy,
    rank_rooms,
    RoomScore,
    CriterionScore,
    AggregationMethod,
)


@dataclass
class RoomData:
    room_id: str
    room_name: str
    temperature: Optional[float] = None
    co2: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[float] = None
    noise: Optional[float] = None
    voc: Optional[float] = None
    air_quality: Optional[float] = None
    seating_capacity: int = 0
    has_projector: bool = False
    computers: int = 0
    has_robots: bool = False


@dataclass
class UserRequirements:
    required_seats: int = 0
    need_projector: bool = False
    need_computers: int = 0
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None


@dataclass
class AHPResult:
    rankings: List[RoomScore]
    weights: Dict[str, float]
    main_criteria_weights: Dict[str, float]
    consistency_ratios: Dict[str, float]
    is_consistent: bool
    evaluation_time: datetime = field(default_factory=datetime.now)


class AHPEngine:
    MAIN_CRITERIA = ["Comfort", "Health", "Usability"]
    
    SUB_CRITERIA = {
        "Comfort": ["Temperature", "Lighting", "Noise", "Humidity"],
        "Health": ["CO2", "AirQuality", "VOC"],
        "Usability": ["SeatingCapacity", "Equipment", "AVFacilities"],
    }

    RAW_VALUE_ATTR = {
        "Temperature": "temperature",
        "Lighting": "light",
        "Noise": "noise",
        "Humidity": "humidity",
        "CO2": "co2",
        "AirQuality": "air_quality",
        "VOC": "voc",
        "SeatingCapacity": "seating_capacity",
        "Equipment": "computers",
        "AVFacilities": "has_projector",
    }
    
    def __init__(self):
        self._main_matrix: Optional[PairwiseMatrix] = None
        self._sub_matrices: Dict[str, PairwiseMatrix] = {}
        
        self._main_weights: Dict[str, float] = {}
        self._sub_weights: Dict[str, Dict[str, float]] = {}
        self._global_weights: Dict[str, float] = {}
        
        self._rooms: List[RoomData] = []
        self._requirements: UserRequirements = UserRequirements()
        
        self._consistency_ratios: Dict[str, float] = {}
        self._is_consistent: bool = True
        
        self._initialize_default_weights()
    
    def _initialize_default_weights(self):
        self._main_matrix = create_default_criteria_matrix()
        self._main_weights = self._calculate_weights(
            self._main_matrix, "main"
        )
        
        self._sub_matrices["Comfort"] = create_comfort_subcriteria_matrix()
        self._sub_matrices["Health"] = create_health_subcriteria_matrix()
        self._sub_matrices["Usability"] = create_usability_subcriteria_matrix()
        
        for main_crit in self.MAIN_CRITERIA:
            if main_crit in self._sub_matrices:
                self._sub_weights[main_crit] = self._calculate_weights(
                    self._sub_matrices[main_crit], main_crit
                )
        
        self._calculate_global_weights()
    
    def _calculate_weights(
        self, 
        matrix: PairwiseMatrix, 
        name: str
    ) -> Dict[str, float]:
        np_matrix = matrix.get_matrix()
        weights = calculate_priority_weights(np_matrix)
        
        cr, is_consistent = calculate_consistency_ratio(np_matrix)
        self._consistency_ratios[name] = cr
        
        if not is_consistent:
            self._is_consistent = False
        
        return dict(zip(matrix.criteria, weights))
    
    def _calculate_global_weights(self):
        self._global_weights = {}
        
        for main_crit, main_weight in self._main_weights.items():
            if main_crit in self._sub_weights:
                for sub_crit, sub_weight in self._sub_weights[main_crit].items():
                    self._global_weights[sub_crit] = main_weight * sub_weight
    
    def set_user_preferences(
        self,
        main_comparisons: Optional[Dict[tuple, float]] = None,
        sub_comparisons: Optional[Dict[str, Dict[tuple, float]]] = None
    ):
        self._is_consistent = True

        if main_comparisons:
            for (crit_a, crit_b), value in main_comparisons.items():
                self._main_matrix.set_comparison(crit_a, crit_b, value)
            self._main_weights = self._calculate_weights(
                self._main_matrix, "main"
            )
        
        if sub_comparisons:
            for main_crit, comparisons in sub_comparisons.items():
                if main_crit not in self._sub_matrices:
                    continue
                for (crit_a, crit_b), value in comparisons.items():
                    self._sub_matrices[main_crit].set_comparison(crit_a, crit_b, value)
                self._sub_weights[main_crit] = self._calculate_weights(
                    self._sub_matrices[main_crit], main_crit
                )
    
        self._calculate_global_weights()
        self._is_consistent = all(cr < 0.1 for cr in self._consistency_ratios.values())
    
    def set_requirements(self, requirements: UserRequirements):
        self._requirements = requirements
    
    def load_room_data(self, rooms: List[RoomData]):
        self._rooms = rooms
    
    def load_room_data_from_dict(self, rooms_data: List[Dict[str, Any]]):
        self._rooms = []
        for data in rooms_data:
            facilities = data.get("facilities", {}) or {}

            room = RoomData(
                room_id=data.get("id") or data.get("room_id") or data.get("name", ""),
                room_name=data.get("name") or data.get("room_id") or data.get("id", ""),
                temperature=data.get("temperature"),
                co2=data.get("co2"),
                humidity=data.get("humidity"),
                light=data.get("light"),
                noise=data.get("noise"),
                voc=data.get("voc"),
                air_quality=data.get("air_quality"),
                seating_capacity=data.get("seating_capacity", facilities.get("seating_capacity", 0)),
                has_projector=bool(data.get("has_projector", facilities.get("videoprojector", False))),
                computers=data.get("computers", facilities.get("computers", 0)),
                has_robots=bool(data.get("has_robots", facilities.get("robots_for_training", 0))),
            )
            self._rooms.append(room)
    
    def _score_room(self, room: RoomData) -> Dict[str, float]:
        scores = {}
        
        if room.temperature is not None:
            scores["Temperature"] = map_temperature(room.temperature)
        else:
            scores["Temperature"] = 0.5
        
        if room.light is not None:
            scores["Lighting"] = map_light(room.light)
        else:
            scores["Lighting"] = 0.5
        
        if room.noise is not None:
            scores["Noise"] = map_noise(room.noise)
        else:
            scores["Noise"] = 0.5
        
        if room.humidity is not None:
            scores["Humidity"] = map_humidity(room.humidity)
        else:
            scores["Humidity"] = 0.5
        
        if room.co2 is not None:
            scores["CO2"] = map_co2(room.co2)
        else:
            scores["CO2"] = 0.5
        
        if room.air_quality is not None:
            scores["AirQuality"] = map_air_quality(room.air_quality)
        else:
            scores["AirQuality"] = 0.5
        
        if room.voc is not None:
            scores["VOC"] = map_voc(room.voc)
        else:
            scores["VOC"] = 0.5
        
        scores["SeatingCapacity"] = map_seating_capacity(
            room.seating_capacity, 
            self._requirements.required_seats
        )
        
        scores["Equipment"] = map_equipment(
            room.computers > 0,
            room.computers,
            self._requirements.need_computers
        )
        
        scores["AVFacilities"] = map_av_facilities(
            room.has_projector,
            self._requirements.need_projector
        )
        
        return scores
    
    def evaluate_rooms(
        self,
        method: AggregationMethod = AggregationMethod.WEIGHTED_SUM
    ) -> AHPResult:
        if not self._rooms:
            raise ValueError("No rooms loaded. Call load_room_data() first.")
        
        room_scores = []
        
        hierarchy_weights = {
            "main": self._main_weights,
        }
        hierarchy_weights.update(self._sub_weights)
        
        for room in self._rooms:
            leaf_scores = self._score_room(room)
            
            final_score, main_scores = aggregate_with_hierarchy(
                leaf_scores, hierarchy_weights, method
            )
            
            room_score = RoomScore(
                room_id=room.room_id,
                room_name=room.room_name,
                final_score=final_score,
                comfort_score=main_scores.get("Comfort", 0),
                health_score=main_scores.get("Health", 0),
                usability_score=main_scores.get("Usability", 0),
            )
            
            for crit_id, score in leaf_scores.items():
                attr_name = self.RAW_VALUE_ATTR.get(crit_id)
                raw_value = getattr(room, attr_name, 0) if attr_name else 0

                room_score.criterion_scores.append(CriterionScore(
                    criterion_id=crit_id,
                    criterion_name=crit_id,
                    raw_value=raw_value,
                    normalized_score=score,
                    weight=self._global_weights.get(crit_id, 0),
                ))
            
            room_scores.append(room_score)
        
        ranked_rooms = rank_rooms(room_scores)
        
        return AHPResult(
            rankings=ranked_rooms,
            weights=self._global_weights,
            main_criteria_weights=self._main_weights,
            consistency_ratios=self._consistency_ratios,
            is_consistent=self._is_consistent,
        )
    
    def get_weights_summary(self) -> str:
        lines = ["=" * 40, "AHP WEIGHTS SUMMARY", "=" * 40, ""]
        
        lines.append("MAIN CRITERIA:")
        for crit, weight in self._main_weights.items():
            lines.append(f"  {crit}: {weight:.4f} ({weight*100:.1f}%)")
        
        lines.append("\nSUB-CRITERIA:")
        for main_crit, sub_weights in self._sub_weights.items():
            lines.append(f"\n  {main_crit}:")
            for sub_crit, weight in sub_weights.items():
                global_w = self._global_weights.get(sub_crit, 0)
                lines.append(f"    {sub_crit}: {weight:.4f} (global: {global_w:.4f})")
        
        lines.append("\nCONSISTENCY RATIOS:")
        for name, cr in self._consistency_ratios.items():
            status = "OK" if cr < 0.1 else "FAIL"
            lines.append(f"  {name}: {cr:.4f} {status}")
        
        return "\n".join(lines)
