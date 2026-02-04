from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from app.auth import get_current_active_user
from app.database import db
from app.models.room import (
    RoomResponse,
    RoomListResponse,
    RoomFacilities,
)
from app.models.sensor import SensorType

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=RoomListResponse,
    summary="List all rooms",
    description="Get a list of all available rooms with their facilities."
)
async def list_rooms(
    include_conditions: bool = Query(
        False,
        description="Include current environmental sensor readings"
    ),
    videoprojector: Optional[bool] = Query(
        None,
        description="Filter rooms with/without video projector"
    ),
    min_seating: Optional[int] = Query(
        None,
        ge=1,
        description="Minimum seating capacity required"
    )
):
    """List all rooms with optional filtering."""
    try:
        query_filter = {}
        if videoprojector is not None:
            query_filter["facilities.videoprojector"] = videoprojector
        if min_seating is not None:
            query_filter["facilities.seating_capacity"] = {"$gte": min_seating}

        collection = db.get_collection("rooms")
        cursor = collection.find(query_filter)
        rooms_list = await cursor.to_list(length=100)

        if not rooms_list:
            return RoomListResponse(rooms=[], total=0)

        rooms = []
        for room_doc in rooms_list:
            room_data = {
                "name": room_doc["name"],
                "facilities": room_doc["facilities"],
                "building": room_doc.get("building"),
                "floor": room_doc.get("floor")
            }

            if include_conditions:
                conditions = await _get_current_conditions(room_doc["name"])
                room_data["current_conditions"] = conditions

            rooms.append(RoomResponse(**room_data))

        return RoomListResponse(
            rooms=rooms,
            total=len(rooms)
        )

    except Exception as e:
        logger.error(f"Error listing rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Get room details",
    description="Get detailed information about a specific room."
)
async def get_room(
    room_id: str,
    include_conditions: bool = Query(
        False,
        description="Include current environmental sensor readings"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Get details for a specific room."""
    try:
        collection = db.get_collection("rooms")
        room_doc = await collection.find_one({"name": room_id})

        if not room_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Room '{room_id}' not found"
            )

        room_data = {
            "name": room_doc["name"],
            "facilities": room_doc["facilities"],
            "building": room_doc.get("building"),
            "floor": room_doc.get("floor")
        }

        if include_conditions:
            conditions = await _get_current_conditions(room_id)
            room_data["current_conditions"] = conditions

        return RoomResponse(**room_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{room_id}/facilities",
    response_model=RoomFacilities,
    summary="Get room facilities only",
    description="Get only the facilities information for a room."
)
async def get_room_facilities(room_id: str, current_user: dict = Depends(get_current_active_user)):
    """Get only the facilities for a specific room."""
    try:
        collection = db.get_collection("rooms")
        room_doc = await collection.find_one(
            {"name": room_id},
            {"facilities": 1}
        )

        if not room_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Room '{room_id}' not found"
            )

        return RoomFacilities(**room_doc["facilities"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching facilities for {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _get_current_conditions(room_name: str) -> dict:
    """Helper to get the latest sensor readings for a room."""
    try:
        collection = db.get_collection("sensor_readings")

        pipeline = [
            {"$match": {"room_name": room_name}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$sensor_type",
                    "value": {"$first": "$value"},
                    "timestamp": {"$first": "$timestamp"}
                }
            }
        ]

        results = await collection.aggregate(pipeline).to_list(length=10)

        conditions = {}
        for doc in results:
            sensor_type = doc["_id"]
            conditions[sensor_type] = doc["value"]

        return conditions if conditions else None

    except Exception as e:
        logger.warning(f"Could not fetch current conditions for {room_name}: {e}")
        return None
