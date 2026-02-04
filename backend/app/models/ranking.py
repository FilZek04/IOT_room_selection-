from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class SaatyScale(int, Enum):
    """
    Saaty scale for AHP pairwise comparisons.

    Scale values:
    - 1: Equal importance
    - 3: Moderate importance
    - 5: Strong importance
    - 7: Very strong importance
    - 9: Extreme importance
    """
    EQUAL = 1
    MODERATE = 3
    STRONG = 5
    VERY_STRONG = 7
    EXTREME = 9


class CriteriaWeights(BaseModel):
    """
    User preference weights for decision criteria.

    These weights determine the relative importance of each factor
    in the room selection decision. Uses Saaty scale (1-9).
    """
    temperature: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of temperature comfort (1-9 Saaty scale)"
    )
    co2: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of air quality/CO2 levels (1-9)"
    )
    humidity: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of humidity levels (1-9)"
    )
    sound: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of noise levels (1-9)"
    )
    facilities: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of room facilities (1-9)"
    )
    availability: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Importance of calendar availability (1-9)"
    )

    @field_validator('temperature', 'co2', 'humidity', 'sound', 'facilities', 'availability')
    @classmethod
    def validate_saaty_scale(cls, v):
        """Ensure weights follow Saaty scale (1, 3, 5, 7, 9)."""
        valid_values = [1, 3, 5, 7, 9]
        if v not in valid_values:
            raise ValueError(f"Weight must be one of {valid_values} (Saaty scale)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 5,
                "co2": 7,
                "humidity": 3,
                "sound": 5,
                "facilities": 9,
                "availability": 9
            }
        }


class EnvironmentalPreferences(BaseModel):
    """
    User's desired environmental conditions.

    The system will rank rooms based on how closely they match these preferences.
    """
    temperature_min: Optional[float] = Field(
        None,
        ge=15.0,
        le=30.0,
        description="Minimum acceptable temperature (°C)"
    )
    temperature_max: Optional[float] = Field(
        None,
        ge=15.0,
        le=30.0,
        description="Maximum acceptable temperature (°C)"
    )
    co2_max: Optional[float] = Field(
        None,
        ge=400.0,
        le=2000.0,
        description="Maximum acceptable CO2 level (ppm)"
    )
    humidity_min: Optional[float] = Field(
        None,
        ge=20.0,
        le=80.0,
        description="Minimum acceptable humidity (%)"
    )
    humidity_max: Optional[float] = Field(
        None,
        ge=20.0,
        le=80.0,
        description="Maximum acceptable humidity (%)"
    )
    sound_max: Optional[float] = Field(
        None,
        ge=30.0,
        le=100.0,
        description="Maximum acceptable sound level (dB)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "temperature_min": 19.0,
                "temperature_max": 22.0,
                "co2_max": 800.0,
                "humidity_min": 40.0,
                "humidity_max": 60.0,
                "sound_max": 50.0
            }
        }


class FacilityRequirements(BaseModel):
    """
    Required room facilities.

    Rooms not meeting these requirements will be filtered out.
    """
    videoprojector: Optional[bool] = Field(None, description="Requires projector")
    min_seating: Optional[int] = Field(None, ge=1, description="Minimum seating capacity")
    computers: Optional[bool] = Field(None, description="Requires computers")
    whiteboard: Optional[bool] = Field(None, description="Requires whiteboard")
    min_training_robots: Optional[int] = Field(None, ge=0, description="Minimum training robots")

    class Config:
        json_schema_extra = {
            "example": {
                "videoprojector": True,
                "min_seating": 30,
                "computers": False,
                "whiteboard": True,
                "min_training_robots": 2
            }
        }


class RankingRequest(BaseModel):
    """
    Request body for room ranking endpoint.

    Users submit their preferences and the system returns ranked rooms.
    """
    criteria_weights: CriteriaWeights = Field(
        ...,
        description="Relative importance of each criterion (Saaty scale)"
    )
    environmental_preferences: Optional[EnvironmentalPreferences] = Field(
        None,
        description="Desired environmental conditions"
    )
    facility_requirements: Optional[FacilityRequirements] = Field(
        None,
        description="Required room facilities"
    )
    requested_time: Optional[datetime] = Field(
        None,
        description="Desired time slot (for availability check)"
    )
    duration_minutes: Optional[int] = Field(
        None,
        ge=15,
        le=480,
        description="Required duration in minutes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "criteria_weights": {
                    "temperature": 5,
                    "co2": 7,
                    "humidity": 3,
                    "sound": 5,
                    "facilities": 9,
                    "availability": 9
                },
                "environmental_preferences": {
                    "temperature_min": 19.0,
                    "temperature_max": 22.0,
                    "co2_max": 800.0
                },
                "facility_requirements": {
                    "videoprojector": True,
                    "min_seating": 30
                },
                "requested_time": "2024-12-22T14:00:00Z",
                "duration_minutes": 120
            }
        }


class RankedRoom(BaseModel):
    """
    A single room with its ranking score and details.
    """
    room_name: str
    rank: int = Field(..., ge=1, description="Ranking position (1 = best)")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="AHP overall score (0-1)")
    criteria_scores: dict = Field(
        ...,
        description="Individual scores for each criterion"
    )
    current_conditions: Optional[dict] = Field(
        None,
        description="Current environmental conditions"
    )
    facilities: dict = Field(..., description="Room facilities")
    is_available: bool = Field(..., description="Available at requested time")

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_3",
                "rank": 1,
                "overall_score": 0.87,
                "criteria_scores": {
                    "temperature": 0.92,
                    "co2": 0.85,
                    "humidity": 0.78,
                    "sound": 0.90,
                    "facilities": 0.95,
                    "availability": 1.0
                },
                "current_conditions": {
                    "temperature": 20.5,
                    "co2": 650,
                    "humidity": 45
                },
                "facilities": {
                    "videoprojector": True,
                    "seating_capacity": 30
                },
                "is_available": True
            }
        }


class RankingResponse(BaseModel):
    """
    Response for ranking request.

    Returns rooms sorted by overall score (best first).
    """
    ranked_rooms: list[RankedRoom] = Field(
        ...,
        description="Rooms sorted by ranking (best first)"
    )
    total_rooms_evaluated: int = Field(..., description="Number of rooms evaluated")
    timestamp: datetime = Field(..., description="When ranking was performed")
    request_summary: dict = Field(..., description="Summary of user preferences")

    class Config:
        json_schema_extra = {
            "example": {
                "ranked_rooms": [
                    {
                        "room_name": "Room_3",
                        "rank": 1,
                        "overall_score": 0.87,
                        "is_available": True
                    }
                ],
                "total_rooms_evaluated": 5,
                "timestamp": "2024-12-22T14:30:00Z",
                "request_summary": {
                    "top_criteria": ["facilities", "availability", "co2"]
                }
            }
        }
