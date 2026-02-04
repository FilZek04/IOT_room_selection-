"""
Grafana-specific API endpoints for dashboard data visualization.

These endpoints return data formatted specifically for Grafana's Infinity plugin,
providing time-series data, current readings, alerts, and facilities information
in a format optimized for dashboard panels.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from app.database import db
from app.models.sensor import SensorType, SensorUnit

logger = logging.getLogger(__name__)
router = APIRouter()

SENSOR_UNITS = {
    SensorType.TEMPERATURE: SensorUnit.CELSIUS,
    SensorType.CO2: SensorUnit.PPM,
    SensorType.HUMIDITY: SensorUnit.PERCENT,
    SensorType.SOUND: SensorUnit.DECIBEL,
    SensorType.VOC: SensorUnit.PPB,
    SensorType.LIGHT_INTENSITY: SensorUnit.LUX,
    SensorType.AIR_QUALITY: SensorUnit.AQI,
}


@router.get(
    "/timeseries",
    summary="Get time-series sensor data for Grafana",
    description="""
    Returns time-series sensor data formatted for Grafana visualization.
    
    This endpoint is optimized for Grafana's Infinity plugin and returns
    data in a table format suitable for time-series graphs.
    
    Query parameters:
    - sensor_type: Type of sensor (temperature, co2, humidity, etc.)
    - room_names: Comma-separated list of room names (optional, defaults to all rooms)
    - hours: Number of hours of historical data to fetch (default: 24)
    - interval_minutes: Data aggregation interval in minutes (default: 5)
    """
)
async def get_timeseries_data(
    sensor_type: SensorType = Query(..., description="Sensor type to query"),
    room_names: Optional[str] = Query(None, description="Comma-separated room names (e.g., 'Room_1,Room_2')"),
    hours: int = Query(24, ge=1, le=168, description="Hours of historical data"),
    interval_minutes: int = Query(5, ge=1, le=60, description="Aggregation interval in minutes")
):
    """
    Get time-series data formatted for Grafana graphs.
    Returns data aggregated by time intervals for smooth visualization.
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Parse room names
        rooms = None
        if room_names:
            rooms = [r.strip() for r in room_names.split(",")]
        else:
            # Get all rooms from database
            rooms_collection = db.get_collection("rooms")
            all_rooms = await rooms_collection.find({}).to_list(length=100)
            rooms = [r["name"] for r in all_rooms]
        
        collection = db.get_collection("sensor_readings")
        results: List[dict] = []

        match_base: dict[str, object] = {"sensor_type": sensor_type.value}
        if rooms:
            match_base["room_name"] = {"$in": rooms}

        recent_exists = await collection.find_one({
            **match_base,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        })

        if recent_exists is None:
            latest = await collection.find(match_base).sort("timestamp", -1).limit(1).to_list(length=1)
            if latest:
                end_time = latest[0]["timestamp"]
                start_time = end_time - timedelta(hours=hours)
        
        for room in rooms:
            # Build aggregation pipeline for time-series data
            match_stage = {
                "room_name": room,
                "sensor_type": sensor_type.value,
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$timestamp"},
                            "month": {"$month": "$timestamp"},
                            "day": {"$dayOfMonth": "$timestamp"},
                            "hour": {"$hour": "$timestamp"},
                            "minute": {
                                "$subtract": [
                                    {"$minute": "$timestamp"},
                                    {"$mod": [{"$minute": "$timestamp"}, interval_minutes]}
                                ]
                            }
                        },
                        "avg_value": {"$avg": "$value"},
                        "min_value": {"$min": "$value"},
                        "max_value": {"$max": "$value"},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            data_points = await collection.aggregate(pipeline).to_list(length=1000)
            
            for point in data_points:
                # Reconstruct timestamp from components
                ts = datetime(
                    point["_id"]["year"],
                    point["_id"]["month"],
                    point["_id"]["day"],
                    point["_id"]["hour"],
                    point["_id"]["minute"]
                )
                
                results.append({
                    "timestamp": ts.isoformat(),
                    "room": room,
                    "value": round(point["avg_value"], 2),
                    "min": round(point["min_value"], 2),
                    "max": round(point["max_value"], 2),
                    "samples": point["count"]
                })
        
        # Sort by timestamp
        results.sort(key=lambda x: x["timestamp"])
        
        return {
            "sensor_type": sensor_type.value,
            "unit": SENSOR_UNITS[sensor_type].value,
            "hours": hours,
            "rooms": rooms,
            "data_points": len(results),
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching timeseries data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/current/all",
    summary="Get current sensor readings for all rooms",
    description="""
    Returns the latest sensor readings for all rooms.
    
    Useful for comparison panels showing current values across all rooms.
    """
)
async def get_all_current_readings(
):
    """
    Get latest readings for all sensors in all rooms.
    Returns data formatted for Grafana tables and stat panels.
    """
    try:
        # Get all rooms
        rooms_collection = db.get_collection("rooms")
        rooms = await rooms_collection.find({}).to_list(length=100)
        
        collection = db.get_collection("sensor_readings")
        results = []
        
        for room in rooms:
            room_name = room["name"]
            
            # Get latest reading for each sensor type
            pipeline = [
                {"$match": {"room_name": room_name}},
                {"$sort": {"timestamp": -1}},
                {
                    "$group": {
                        "_id": "$sensor_type",
                        "value": {"$first": "$value"},
                        "timestamp": {"$first": "$timestamp"},
                        "unit": {"$first": "$unit"}
                    }
                }
            ]
            
            sensor_data = await collection.aggregate(pipeline).to_list(length=10)
            
            room_entry = {
                "room": room_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add facilities info
            facilities = room.get("facilities", {})
            room_entry["seating_capacity"] = facilities.get("seating_capacity", 0)
            room_entry["has_projector"] = facilities.get("videoprojector", False)
            room_entry["has_whiteboard"] = facilities.get("whiteboard", False)
            room_entry["has_air_conditioning"] = facilities.get("air_conditioning", False)
            
            # Add sensor readings
            for sensor in sensor_data:
                sensor_type = sensor["_id"]
                room_entry[sensor_type] = sensor["value"]
                room_entry[f"{sensor_type}_unit"] = sensor["unit"]
                room_entry[f"{sensor_type}_last_updated"] = sensor["timestamp"].isoformat()
            
            results.append(room_entry)
        
        return {
            "total_rooms": len(results),
            "timestamp": datetime.utcnow().isoformat(),
            "rooms": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching current readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/alerts",
    summary="Get sensor health alerts",
    description="""
    Returns sensor health status and alerts for all rooms.
    
    Checks for:
    - Sensors that haven't reported data recently (stale data)
    - Values exceeding threshold limits
    - Missing sensors in rooms
    
    Returns data formatted for Grafana alert panels.
    """
)
async def get_sensor_alerts(
    stale_threshold_minutes: int = Query(30, ge=5, le=120, description="Minutes before considering data stale")
):
    """
    Get sensor health alerts and status for all rooms.
    """
    try:
        # Get all rooms
        rooms_collection = db.get_collection("rooms")
        rooms = await rooms_collection.find({}).to_list(length=100)
        
        collection = db.get_collection("sensor_readings")
        alerts = []
        now = datetime.utcnow()
        stale_threshold = now - timedelta(minutes=stale_threshold_minutes)
        
        # Expected sensor types per room
        expected_sensors = ["temperature", "co2", "humidity", "air_quality"]
        
        # Thresholds for alerting
        thresholds = {
            "temperature": {"min": 18, "max": 28, "unit": "°C"},
            "co2": {"min": 300, "max": 1000, "unit": "ppm"},
            "humidity": {"min": 30, "max": 70, "unit": "%"},
            "air_quality": {"min": 0, "max": 100, "unit": "AQI"}
        }
        
        for room in rooms:
            room_name = room["name"]
            
            # Get latest reading for each sensor type
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
            
            sensor_data = await collection.aggregate(pipeline).to_list(length=10)
            active_sensors = {s["_id"]: s for s in sensor_data}
            
            # Check for missing sensors
            for expected in expected_sensors:
                if expected not in active_sensors:
                    alerts.append({
                        "room": room_name,
                        "sensor_type": expected,
                        "alert_type": "missing",
                        "severity": "warning",
                        "message": f"{expected} sensor not found in {room_name}",
                        "timestamp": now.isoformat(),
                        "status": "No Data"
                    })
            
            # Check for stale data and threshold violations
            for sensor_type, data in active_sensors.items():
                last_reading_time = data["timestamp"]
                value = data["value"]
                
                # Check if data is stale
                if last_reading_time < stale_threshold:
                    alerts.append({
                        "room": room_name,
                        "sensor_type": sensor_type,
                        "alert_type": "stale",
                        "severity": "critical",
                        "message": f"{sensor_type} in {room_name} hasn't reported for {stale_threshold_minutes}+ minutes",
                        "timestamp": now.isoformat(),
                        "last_reading": last_reading_time.isoformat(),
                        "status": "Offline"
                    })
                else:
                    # Check threshold violations
                    if sensor_type in thresholds:
                        thresh = thresholds[sensor_type]
                        if value < thresh["min"] or value > thresh["max"]:
                            severity = "warning" if value < thresh["max"] * 1.2 else "critical"
                            alerts.append({
                                "room": room_name,
                                "sensor_type": sensor_type,
                                "alert_type": "threshold",
                                "severity": severity,
                                "message": f"{sensor_type} in {room_name} is {value} {thresh['unit']} (threshold: {thresh['min']}-{thresh['max']} {thresh['unit']})",
                                "timestamp": now.isoformat(),
                                "value": value,
                                "threshold_min": thresh["min"],
                                "threshold_max": thresh["max"],
                                "status": "Degraded" if severity == "warning" else "Critical"
                            })
        
        # Calculate summary statistics
        critical_count = sum(1 for a in alerts if a["severity"] == "critical")
        warning_count = sum(1 for a in alerts if a["severity"] == "warning")
        offline_count = sum(1 for a in alerts if a["alert_type"] == "stale")
        
        return {
            "timestamp": now.isoformat(),
            "total_alerts": len(alerts),
            "critical": critical_count,
            "warning": warning_count,
            "offline_sensors": offline_count,
            "stale_threshold_minutes": stale_threshold_minutes,
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error fetching sensor alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/facilities/summary",
    summary="Get facilities summary for all rooms",
    description="""
    Returns a summary of all rooms with their facilities and current availability.
    
    Includes:
    - Room facilities (projector, seating, whiteboard, etc.)
    - Current sensor readings
    - Calendar availability status
    
    Formatted for Grafana table panels.
    """
)
async def get_facilities_summary(
):
    """
    Get comprehensive facilities summary for all rooms.
    """
    try:
        # Get all rooms with facilities
        rooms_collection = db.get_collection("rooms")
        rooms = await rooms_collection.find({}).to_list(length=100)
        
        # Get current sensor readings
        sensor_collection = db.get_collection("sensor_readings")
        
        # Check calendar for current availability
        calendar_collection = db.get_collection("calendar_events")
        now = datetime.utcnow()
        
        results = []
        
        for room in rooms:
            room_name = room["name"]
            facilities = room.get("facilities", {})
            
            # Get latest sensor readings
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
            
            sensor_data = await sensor_collection.aggregate(pipeline).to_list(length=10)
            sensors = {s["_id"]: s for s in sensor_data}
            
            # Check if room is currently occupied
            current_event = await calendar_collection.find_one({
                "room_name": room_name,
                "status": "confirmed",
                "start_time": {"$lte": now},
                "end_time": {"$gte": now}
            })
            
            is_occupied = current_event is not None
            
            # Determine comfort level based on sensor readings
            comfort_score = 100
            comfort_issues = []
            
            temp = sensors.get("temperature", {}).get("value")
            if temp is not None:
                if temp < 18 or temp > 26:
                    comfort_score -= 20
                    comfort_issues.append(f"Temperature: {temp}°C")
            
            co2 = sensors.get("co2", {}).get("value")
            if co2 is not None:
                if co2 > 800:
                    comfort_score -= 20
                    comfort_issues.append(f"CO2: {co2}ppm")
                elif co2 > 1000:
                    comfort_score -= 40
            
            humidity = sensors.get("humidity", {}).get("value")
            if humidity is not None:
                if humidity < 30 or humidity > 60:
                    comfort_score -= 10
                    comfort_issues.append(f"Humidity: {humidity}%")
            
            # Build room summary
            room_summary = {
                "room": room_name,
                "building": room.get("building", "Unknown"),
                "floor": room.get("floor", 0),
                "seating_capacity": facilities.get("seating_capacity", 0),
                "has_projector": "✓" if facilities.get("videoprojector") else "✗",
                "has_whiteboard": "✓" if facilities.get("whiteboard") else "✗",
                "has_air_conditioning": "✓" if facilities.get("air_conditioning") else "✗",
                "has_computers": facilities.get("computers", 0),
                "temperature": sensors.get("temperature", {}).get("value"),
                "co2": sensors.get("co2", {}).get("value"),
                "humidity": sensors.get("humidity", {}).get("value"),
                "air_quality": sensors.get("air_quality", {}).get("value"),
                "occupancy": "Occupied" if is_occupied else "Free",
                "current_event": current_event.get("title") if current_event else None,
                "comfort_score": max(0, comfort_score),
                "comfort_status": "Good" if comfort_score >= 80 else "Fair" if comfort_score >= 60 else "Poor"
            }
            
            results.append(room_summary)
        
        return {
            "timestamp": now.isoformat(),
            "total_rooms": len(results),
            "occupied": sum(1 for r in results if r["occupancy"] == "Occupied"),
            "free": sum(1 for r in results if r["occupancy"] == "Free"),
            "rooms": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching facilities summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Grafana datasource health check",
    description="Simple health check endpoint for Grafana datasource configuration."
)
async def grafana_health_check(
):
    """
    Health check for Grafana datasource.
    """
    try:
        # Test database connection
        client = db.client
        if client is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        await client.admin.command("ping")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Grafana datasource is working correctly"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
