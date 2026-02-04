from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.auth import get_current_active_user
from app.database import db
from app.models.calendar import (
    CalendarEventResponse,
    CalendarEvent,
    RoomAvailability,
    EventStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/events",
    response_model=CalendarEventResponse,
    summary="Get calendar events",
    description="Retrieve calendar events (room bookings) within a time range."
)
async def get_events(
    room_name: Optional[str] = Query(
        None,
        description="Filter by room name (e.g., 'Room_1')"
    ),
    start: Optional[datetime] = Query(
        None,
        description="Start of time range (ISO 8601 format)"
    ),
    end: Optional[datetime] = Query(
        None,
        description="End of time range (ISO 8601 format)"
    ),
    status: Optional[EventStatus] = Query(
        None,
        description="Filter by event status"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Get calendar events with optional filtering."""
    try:
        query_filter = {}

        if room_name:
            query_filter["room_name"] = room_name

        if status:
            query_filter["status"] = status.value

        if start or end:
            time_filter = {}
            if start:
                time_filter["end_time"] = {"$gte": start}
            if end:
                time_filter["start_time"] = {"$lte": end}
            query_filter.update(time_filter)

        collection = db.get_collection("calendar_events")
        cursor = collection.find(query_filter).sort("start_time", 1).limit(500)
        events_list = await cursor.to_list(length=500)

        events = [
            CalendarEvent(
                room_name=doc["room_name"],
                event_id=doc.get("event_id"),
                title=doc["title"],
                start_time=doc["start_time"],
                end_time=doc["end_time"],
                status=EventStatus(doc.get("status", "confirmed")),
                organizer=doc.get("organizer"),
                description=doc.get("description"),
                created_at=doc.get("created_at"),
                synced_at=doc.get("synced_at")
            )
            for doc in events_list
        ]

        return CalendarEventResponse(
            events=events,
            total=len(events)
        )

    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/availability/{room_name}",
    response_model=RoomAvailability,
    summary="Check room availability",
    description="Check if a specific room is available at a given time."
)
async def check_availability(
    room_name: str,
    requested_time: datetime = Query(
        ...,
        description="Time to check availability (ISO 8601 format)"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Check if a room is available at a specific time."""
    try:
        collection = db.get_collection("calendar_events")

        current_event_doc = await collection.find_one({
            "room_name": room_name,
            "status": EventStatus.CONFIRMED.value,
            "start_time": {"$lte": requested_time},
            "end_time": {"$gte": requested_time}
        })

        is_available = current_event_doc is None
        current_event = None
        next_available = None

        if current_event_doc:
            current_event = CalendarEvent(
                room_name=current_event_doc["room_name"],
                event_id=current_event_doc.get("event_id"),
                title=current_event_doc["title"],
                start_time=current_event_doc["start_time"],
                end_time=current_event_doc["end_time"],
                status=EventStatus(current_event_doc.get("status", "confirmed")),
                organizer=current_event_doc.get("organizer")
            )
            next_available = current_event_doc["end_time"]

            next_event = await collection.find_one({
                "room_name": room_name,
                "status": EventStatus.CONFIRMED.value,
                "start_time": {"$lte": current_event_doc["end_time"]},
                "end_time": {"$gt": current_event_doc["end_time"]}
            })

            if next_event:
                next_available = next_event["end_time"]

        return RoomAvailability(
            room_name=room_name,
            requested_time=requested_time,
            is_available=is_available,
            current_event=current_event,
            next_available=next_available
        )

    except Exception as e:
        logger.error(f"Error checking availability for {room_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/availability/{room_name}/range",
    summary="Check availability for time range",
    description="Check if a room is available for a continuous time range."
)
async def check_availability_range(
    room_name: str,
    start_time: datetime = Query(
        ...,
        description="Start of desired time slot (ISO 8601)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="End of desired time slot (ISO 8601)"
    ),
    duration_minutes: Optional[int] = Query(
        None,
        ge=15,
        le=480,
        description="Duration in minutes (alternative to end_time)"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Check if a room is available for a continuous time range."""
    try:
        if not end_time and duration_minutes:
            end_time = start_time + timedelta(minutes=duration_minutes)
        elif not end_time:
            raise HTTPException(
                status_code=400,
                detail="Either end_time or duration_minutes must be provided"
            )

        collection = db.get_collection("calendar_events")
        cursor = collection.find({
            "room_name": room_name,
            "status": EventStatus.CONFIRMED.value,
            "$or": [
                {
                    "start_time": {"$gte": start_time, "$lt": end_time}
                },
                {
                    "end_time": {"$gt": start_time, "$lte": end_time}
                },
                {
                    "start_time": {"$lte": start_time},
                    "end_time": {"$gte": end_time}
                }
            ]
        })

        conflicting_events = await cursor.to_list(length=100)

        is_available = len(conflicting_events) == 0

        conflicts = [
            {
                "title": event["title"],
                "start_time": event["start_time"].isoformat(),
                "end_time": event["end_time"].isoformat(),
                "organizer": event.get("organizer")
            }
            for event in conflicting_events
        ]

        return {
            "room_name": room_name,
            "requested_start": start_time.isoformat(),
            "requested_end": end_time.isoformat(),
            "is_available": is_available,
            "conflicting_events": conflicts,
            "conflict_count": len(conflicts)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking availability range for {room_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
