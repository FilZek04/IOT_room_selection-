from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RoomFacilities(BaseModel):
    """
    Room facilities and equipment.

    Flexible schema - not all fields are required for all rooms.
    """
    videoprojector: bool = Field(default=False, description="Has video projector")
    seating_capacity: int = Field(..., ge=1, description="Number of seats available")
    computers: Optional[int] = Field(None, ge=0, description="Number of computers")
    robots_for_training: Optional[int] = Field(None, ge=0, description="Number of training robots")
    whiteboard: Optional[bool] = Field(None, description="Has whiteboard")
    audio_system: Optional[bool] = Field(None, description="Has audio/speaker system")
    air_conditioning: Optional[bool] = Field(None, description="Has air conditioning")
    windows: Optional[bool] = Field(None, description="Has windows (natural light)")

    class Config:
        json_schema_extra = {
            "example": {
                "videoprojector": True,
                "seating_capacity": 62,
                "computers": 20,
                "whiteboard": True,
                "air_conditioning": True
            }
        }


class Room(BaseModel):
    """
    Room document with metadata and facilities.
    """
    name: str = Field(..., description="Unique room identifier (e.g., 'Room_1')")
    facilities: RoomFacilities
    building: Optional[str] = Field(None, description="Building name or code")
    floor: Optional[int] = Field(None, description="Floor number")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Room_1",
                "facilities": {
                    "videoprojector": True,
                    "seating_capacity": 62,
                    "computers": 20,
                    "whiteboard": True
                },
                "building": "Building A",
                "floor": 2
            }
        }


class RoomResponse(BaseModel):
    """
    Response model for room queries.

    Includes facilities and optional current environmental stats.
    """
    name: str
    facilities: RoomFacilities
    building: Optional[str] = None
    floor: Optional[int] = None
    current_conditions: Optional[dict] = Field(
        None,
        description="Latest sensor readings (temperature, CO2, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Room_1",
                "facilities": {
                    "videoprojector": True,
                    "seating_capacity": 62,
                    "computers": 20
                },
                "building": "Building A",
                "floor": 2,
                "current_conditions": {
                    "temperature": 22.5,
                    "co2": 650,
                    "humidity": 45
                }
            }
        }


class RoomListResponse(BaseModel):
    """Response model for listing multiple rooms."""
    rooms: list[RoomResponse]
    total: int = Field(..., description="Total number of rooms")

    class Config:
        json_schema_extra = {
            "example": {
                "rooms": [
                    {
                        "name": "Room_1",
                        "facilities": {
                            "videoprojector": True,
                            "seating_capacity": 62
                        }
                    }
                ],
                "total": 1
            }
        }
