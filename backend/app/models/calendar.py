from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class EventStatus(str, Enum):
    """Calendar event status."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class CalendarEvent(BaseModel):
    """
    Calendar event representing room booking/availability.

    Synced from University calendar (e.g., Google Calendar API).
    """
    room_name: str = Field(..., description="Room identifier")
    event_id: Optional[str] = Field(None, description="External calendar event ID")
    title: str = Field(..., description="Event title (e.g., 'CS101 Lecture')")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    status: EventStatus = Field(default=EventStatus.CONFIRMED, description="Event status")
    organizer: Optional[str] = Field(None, description="Event organizer email")
    description: Optional[str] = Field(None, description="Event description")
    created_at: Optional[datetime] = Field(None, description="When event was created in DB")
    synced_at: Optional[datetime] = Field(None, description="Last sync from calendar API")

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_1",
                "event_id": "google_cal_123456",
                "title": "CS101 Introduction to Programming",
                "start_time": "2024-12-22T14:00:00Z",
                "end_time": "2024-12-22T16:00:00Z",
                "status": "confirmed",
                "organizer": "prof.smith@uni.lu"
            }
        }


class CalendarEventResponse(BaseModel):
    """Response model for calendar event queries."""
    events: list[CalendarEvent]
    total: int = Field(..., description="Total number of events")

    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "room_name": "Room_1",
                        "title": "CS101 Lecture",
                        "start_time": "2024-12-22T14:00:00Z",
                        "end_time": "2024-12-22T16:00:00Z",
                        "status": "confirmed"
                    }
                ],
                "total": 1
            }
        }


class RoomAvailability(BaseModel):
    """
    Room availability status at a specific time.

    Used for quick availability checks.
    """
    room_name: str
    requested_time: datetime
    is_available: bool
    current_event: Optional[CalendarEvent] = Field(
        None,
        description="Current event occupying the room (if unavailable)"
    )
    next_available: Optional[datetime] = Field(
        None,
        description="When the room becomes available next"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_1",
                "requested_time": "2024-12-22T14:30:00Z",
                "is_available": False,
                "current_event": {
                    "title": "CS101 Lecture",
                    "start_time": "2024-12-22T14:00:00Z",
                    "end_time": "2024-12-22T16:00:00Z"
                },
                "next_available": "2024-12-22T16:00:00Z"
            }
        }
