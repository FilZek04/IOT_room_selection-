from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from typing import Optional
import logging

from app.auth import get_current_active_user
from app.database import db
from app.models.sensor import (
    SensorType,
    SensorUnit,
    SensorReadingResponse,
    SensorStatsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

SENSOR_UNITS = {
    SensorType.TEMPERATURE: SensorUnit.CELSIUS,
    SensorType.CO2: SensorUnit.PPM,
    SensorType.HUMIDITY: SensorUnit.PERCENT,
    SensorType.SOUND: SensorUnit.DECIBEL,
    SensorType.VOC: SensorUnit.PPB,
    SensorType.LIGHT_INTENSITY: SensorUnit.LUX,
}


@router.get(
    "/{room_id}/latest",
    summary="Get latest readings for all sensors",
    description="Get the most recent reading for each sensor type in a room."
)
async def get_latest_readings(room_id: str, current_user: dict = Depends(get_current_active_user)):
    """Get the latest reading for each sensor type in a room."""
    try:
        collection = db.get_collection("sensor_readings")

        pipeline = [
            {"$match": {"room_name": room_id}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$sensor_type",
                    "latest_value": {"$first": "$value"},
                    "latest_timestamp": {"$first": "$timestamp"},
                    "unit": {"$first": "$unit"}
                }
            }
        ]

        results = await collection.aggregate(pipeline).to_list(length=10)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No sensor data found for {room_id}"
            )

        latest_readings = {
            doc["_id"]: {
                "value": doc["latest_value"],
                "timestamp": doc["latest_timestamp"].isoformat(),
                "unit": doc["unit"]
            }
            for doc in results
        }

        return {
            "room_name": room_id,
            "readings": latest_readings,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{room_id}/{sensor_type}",
    response_model=SensorReadingResponse,
    summary="Get sensor readings for a room",
    description="Retrieve sensor readings for a specific room and sensor type within a time range."
)
async def get_sensor_readings(
    room_id: str,
    sensor_type: SensorType,
    start: Optional[datetime] = Query(
        None,
        description="Start timestamp (ISO 8601 format)"
    ),
    end: Optional[datetime] = Query(
        None,
        description="End timestamp (ISO 8601 format)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of readings to return"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Get sensor readings for a specific room and time range."""
    try:
        query_filter = {
            "room_name": room_id,
            "sensor_type": sensor_type.value
        }

        if start or end:
            query_filter["timestamp"] = {}
            if start:
                query_filter["timestamp"]["$gte"] = start
            if end:
                query_filter["timestamp"]["$lte"] = end

        collection = db.get_collection("sensor_readings")
        cursor = collection.find(query_filter).sort("timestamp", -1).limit(limit)
        readings_list = await cursor.to_list(length=limit)

        if not readings_list:
            raise HTTPException(
                status_code=404,
                detail=f"No {sensor_type.value} readings found for {room_id} in the specified time range"
            )

        readings = [
            {
                "timestamp": doc["timestamp"].isoformat(),
                "value": doc["value"]
            }
            for doc in readings_list
        ]

        values = [doc["value"] for doc in readings_list]
        average = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)

        return SensorReadingResponse(
            room_name=room_id,
            sensor_type=sensor_type,
            readings=readings,
            count=len(readings),
            average=average,
            min_value=min_value,
            max_value=max_value,
            unit=SENSOR_UNITS[sensor_type]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sensor readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{room_id}/{sensor_type}/stats",
    response_model=SensorStatsResponse,
    summary="Get aggregated sensor statistics",
    description="Get aggregated statistics for sensor data over a time period."
)
async def get_sensor_stats(
    room_id: str,
    sensor_type: SensorType,
    start: Optional[datetime] = Query(
        None,
        description="Start timestamp (ISO 8601)"
    ),
    end: Optional[datetime] = Query(
        None,
        description="End timestamp (ISO 8601)"
    ),
    current_user: dict = Depends(get_current_active_user)
):
    """Get aggregated statistics for sensor data."""
    try:
        match_stage = {
            "room_name": room_id,
            "sensor_type": sensor_type.value
        }

        if start or end:
            match_stage["timestamp"] = {}
            if start:
                match_stage["timestamp"]["$gte"] = start
            if end:
                match_stage["timestamp"]["$lte"] = end

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "average": {"$avg": "$value"},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                    "std_deviation": {"$stdDevPop": "$value"},
                    "sample_count": {"$sum": 1},
                    "first_timestamp": {"$min": "$timestamp"},
                    "last_timestamp": {"$max": "$timestamp"}
                }
            }
        ]

        collection = db.get_collection("sensor_readings")
        result = await collection.aggregate(pipeline).to_list(length=1)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No {sensor_type.value} data found for {room_id} in the specified time range"
            )

        stats = result[0]

        return SensorStatsResponse(
            room_name=room_id,
            sensor_type=sensor_type,
            time_range={
                "start": stats["first_timestamp"].isoformat(),
                "end": stats["last_timestamp"].isoformat()
            },
            average=stats["average"],
            min_value=stats["min_value"],
            max_value=stats["max_value"],
            std_deviation=stats.get("std_deviation"),
            unit=SENSOR_UNITS[sensor_type],
            sample_count=stats["sample_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sensor stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
