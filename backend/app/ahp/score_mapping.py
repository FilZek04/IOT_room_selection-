"""Score mapping functions for AHP algorithm. Maps raw sensor values to normalized scores (0-1) based on EU standards."""

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import numpy as np


@dataclass
class MappingConfig:
    name: str
    unit: str
    optimal_min: float
    optimal_max: float
    acceptable_min: float
    acceptable_max: float
    description: str


TEMPERATURE_CONFIG = MappingConfig(
    name="Temperature",
    unit="°C",
    optimal_min=20.0,
    optimal_max=24.0,
    acceptable_min=18.0,
    acceptable_max=26.0,
    description="Based on EN 16798-1, Category II for office spaces"
)

CO2_CONFIG = MappingConfig(
    name="CO2",
    unit="ppm",
    optimal_min=0.0,
    optimal_max=600.0,
    acceptable_min=0.0,
    acceptable_max=1000.0,
    description="Based on EN 16798-1, Category II (800 ppm above outdoor ~400)"
)

HUMIDITY_CONFIG = MappingConfig(
    name="Humidity",
    unit="%RH",
    optimal_min=40.0,
    optimal_max=60.0,
    acceptable_min=30.0,
    acceptable_max=70.0,
    description="Based on EN 16798-1 and health research"
)

LIGHT_CONFIG = MappingConfig(
    name="Light Intensity",
    unit="lux",
    optimal_min=300.0,
    optimal_max=500.0,
    acceptable_min=200.0,
    acceptable_max=750.0,
    description="Based on EN 12464-1 for office/classroom lighting"
)

NOISE_CONFIG = MappingConfig(
    name="Noise",
    unit="dBA",
    optimal_min=0.0,
    optimal_max=35.0,
    acceptable_min=0.0,
    acceptable_max=45.0,
    description="Based on WHO guidelines and EN 16798-1"
)

VOC_CONFIG = MappingConfig(
    name="VOC",
    unit="ppb",
    optimal_min=0.0,
    optimal_max=200.0,
    acceptable_min=0.0,
    acceptable_max=400.0,
    description="Based on WELL Building Standard"
)

AIR_QUALITY_CONFIG = MappingConfig(
    name="Air Quality Index",
    unit="AQI",
    optimal_min=0.0,
    optimal_max=50.0,
    acceptable_min=0.0,
    acceptable_max=100.0,
    description="US EPA AQI scale adapted for indoor use"
)

OCCUPANCY_CONFIG = MappingConfig(
    name="Occupancy",
    unit="count",
    optimal_min=0.0,
    optimal_max=10.0,  # Low occupancy is optimal for focused work
    acceptable_min=0.0,
    acceptable_max=25.0,
    description="Person count from Vision AI - lower is better for focused work"
)


def map_temperature(value: float, config: MappingConfig = TEMPERATURE_CONFIG) -> float:
    """Map temperature (°C) to comfort score (0-1)."""
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_co2(value: float, config: MappingConfig = CO2_CONFIG) -> float:
    """Map CO2 concentration (ppm) to health score (0-1). Lower is better."""
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_humidity(value: float, config: MappingConfig = HUMIDITY_CONFIG) -> float:
    """Map relative humidity (%) to comfort score (0-1)."""
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_light(value: float, config: MappingConfig = LIGHT_CONFIG) -> float:
    """Map light intensity (lux) to comfort score (0-1)."""
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_noise(value: float, config: MappingConfig = NOISE_CONFIG) -> float:
    """Map noise level (dBA) to comfort score (0-1). Lower is better."""
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_voc(value: float, config: MappingConfig = VOC_CONFIG) -> float:
    """Map VOC concentration (ppb) to health score (0-1). Lower is better."""
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_air_quality(value: float, config: MappingConfig = AIR_QUALITY_CONFIG) -> float:
    """Map Air Quality Index to health score (0-1). Lower is better."""
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_occupancy(value: float, room_capacity: int = 30, config: MappingConfig = OCCUPANCY_CONFIG) -> float:
    """
    Map occupancy count to usability score (0-1).

    Scoring logic:
    - Empty room (0): Score 1.0 (best for focused work)
    - Up to 33% capacity: Score 0.8-1.0 (good)
    - 33-66% capacity: Score 0.5-0.8 (moderate)
    - 66-100% capacity: Score 0.2-0.5 (crowded)
    - Over capacity: Score 0.0-0.2 (very crowded)

    Args:
        value: Current person count
        room_capacity: Maximum room capacity (default 30)
        config: Mapping configuration

    Returns:
        Score between 0 and 1
    """
    if value <= 0:
        return 1.0

    if room_capacity <= 0:
        room_capacity = 30  # Default fallback

    occupancy_ratio = value / room_capacity

    if occupancy_ratio <= 0.33:
        # Low occupancy: 0.8 to 1.0
        return 1.0 - (occupancy_ratio / 0.33) * 0.2
    elif occupancy_ratio <= 0.66:
        # Moderate occupancy: 0.5 to 0.8
        return 0.8 - ((occupancy_ratio - 0.33) / 0.33) * 0.3
    elif occupancy_ratio <= 1.0:
        # High occupancy: 0.2 to 0.5
        return 0.5 - ((occupancy_ratio - 0.66) / 0.34) * 0.3
    else:
        # Over capacity: 0.0 to 0.2
        over_ratio = min(occupancy_ratio - 1.0, 0.5)  # Cap at 50% over
        return max(0.0, 0.2 - (over_ratio / 0.5) * 0.2)


def map_seating_capacity(value: int, required: int) -> float:
    """Map seating capacity relative to required seats. Returns score 0-1."""
    if required <= 0:
        return 1.0 if value > 0 else 0.5
    
    ratio = value / required
    
    if ratio < 0.5:
        return 0.0
    if ratio < 0.8:
        return max(0.0, 0.5 + (ratio - 0.5) * (0.5 / 0.3))
    if ratio <= 1.5:
        return 1.0
    return max(0.5, 1.0 - (ratio - 1.5) * 0.1)


def map_equipment(has_computers: bool, computer_count: int = 0, required: int = 0) -> float:
    """Map equipment availability to usability score (0-1)."""
    if required == 0:
        return 1.0 if not has_computers else 1.0
    
    if not has_computers or computer_count == 0:
        return 0.0
    
    ratio = computer_count / required
    if ratio >= 1.0:
        return 1.0
    return ratio


def map_av_facilities(has_projector: bool, required: bool = False) -> float:
    """Map A/V facilities availability to score (0-1)."""
    if required and not has_projector:
        return 0.0
    if not required and has_projector:
        return 1.0
    if required and has_projector:
        return 1.0
    return 0.8


def _map_range_centered(
    value: float,
    optimal_min: float,
    optimal_max: float,
    acceptable_min: float,
    acceptable_max: float
) -> float:
    """Map value where optimal range is in the middle."""
    if optimal_min <= value <= optimal_max:
        return 1.0
    
    if acceptable_min <= value < optimal_min:
        range_size = optimal_min - acceptable_min
        if range_size == 0:
            return 0.5
        return 0.5 + 0.5 * (value - acceptable_min) / range_size
    
    if optimal_max < value <= acceptable_max:
        range_size = acceptable_max - optimal_max
        if range_size == 0:
            return 0.5
        return 1.0 - 0.5 * (value - optimal_max) / range_size
    
    if value < acceptable_min:
        distance = acceptable_min - value
        decay = min(1.0, distance / (acceptable_max - acceptable_min))
        return max(0, 0.5 * (1 - decay))
    
    if value > acceptable_max:
        distance = value - acceptable_max
        decay = min(1.0, distance / (acceptable_max - acceptable_min))
        return max(0, 0.5 * (1 - decay))
    
    return 0.0


def _map_lower_is_better(
    value: float,
    optimal_max: float,
    acceptable_max: float
) -> float:
    """Map value where lower is better (0 is optimal)."""
    if value <= 0:
        return 1.0
    
    if value <= optimal_max:
        return 1.0
    
    if value <= acceptable_max:
        range_size = acceptable_max - optimal_max
        if range_size == 0:
            return 0.5
        return 1.0 - 0.5 * (value - optimal_max) / range_size
    
    distance = value - acceptable_max
    decay = min(1.0, distance / acceptable_max)
    return max(0, 0.5 * (1 - decay))


SENSOR_MAPPING_FUNCTIONS: Dict[str, Callable[[float], float]] = {
    "temperature": map_temperature,
    "co2": map_co2,
    "humidity": map_humidity,
    "light": map_light,
    "noise": map_noise,
    "voc": map_voc,
    "air_quality": map_air_quality,
    "occupancy": map_occupancy,
}


def get_mapping_function(sensor_type: str) -> Callable[[float], float]:
    """Get mapping function for sensor type."""
    key = sensor_type.lower().replace(" ", "_").replace("-", "_")
    
    if key not in SENSOR_MAPPING_FUNCTIONS:
        raise ValueError(
            f"Unknown sensor type: {sensor_type}. "
            f"Available: {list(SENSOR_MAPPING_FUNCTIONS.keys())}"
        )
    
    return SENSOR_MAPPING_FUNCTIONS[key]
