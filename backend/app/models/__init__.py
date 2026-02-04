"""
Pydantic models for request/response validation and OpenAPI documentation.

Models are organized by domain:
- sensor: Sensor reading models (temperature, CO2, humidity, etc.)
- room: Room and facilities models
- calendar: Calendar event and availability models
- ranking: AHP ranking request/response models
"""

from app.models.sensor import (
    SensorType,
    SensorUnit,
    SensorReading,
    SensorReadingResponse,
    SensorStatsResponse,
)

from app.models.room import (
    RoomFacilities,
    Room,
    RoomResponse,
    RoomListResponse,
)

from app.models.calendar import (
    EventStatus,
    CalendarEvent,
    CalendarEventResponse,
    RoomAvailability,
)

from app.models.ranking import (
    SaatyScale,
    CriteriaWeights,
    EnvironmentalPreferences,
    FacilityRequirements,
    RankingRequest,
    RankedRoom,
    RankingResponse,
)

__all__ = [
    # Sensor models
    "SensorType",
    "SensorUnit",
    "SensorReading",
    "SensorReadingResponse",
    "SensorStatsResponse",
    # Room models
    "RoomFacilities",
    "Room",
    "RoomResponse",
    "RoomListResponse",
    # Calendar models
    "EventStatus",
    "CalendarEvent",
    "CalendarEventResponse",
    "RoomAvailability",
    # Ranking models
    "SaatyScale",
    "CriteriaWeights",
    "EnvironmentalPreferences",
    "FacilityRequirements",
    "RankingRequest",
    "RankedRoom",
    "RankingResponse",
]
