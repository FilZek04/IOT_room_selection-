from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class SensorType(str, Enum):
    """Supported sensor types."""
    TEMPERATURE = "temperature"
    CO2 = "co2"
    HUMIDITY = "humidity"
    SOUND = "sound"
    VOC = "voc"
    LIGHT_INTENSITY = "light_intensity"
    AIR_QUALITY = "air_quality"
    OCCUPANCY = "occupancy"  # Person count from Vision AI


class SensorUnit(str, Enum):
    """Units for sensor measurements."""
    CELSIUS = "°C"
    PPM = "ppm"  # Parts per million (CO2)
    PERCENT = "%"  # Humidity
    DECIBEL = "dB"  # Sound
    PPB = "ppb"  # Parts per billion (VOC)
    LUX = "lux"  # Light intensity
    AQI = "AQI"  # Air Quality Index
    COUNT = "count"  # Person count (occupancy)


class SensorReading(BaseModel):
    """
    Individual sensor reading document.

    This model represents a single sensor measurement at a specific timestamp.
    """
    room_name: str = Field(..., description="Room identifier (e.g., 'Room_1')")
    sensor_type: SensorType = Field(..., description="Type of sensor measurement")
    value: float = Field(..., description="Measured value")
    unit: SensorUnit = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(..., description="When the measurement was taken")
    created_at: Optional[datetime] = Field(default=None, description="When the record was inserted into DB")

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_1",
                "sensor_type": "temperature",
                "value": 23.4,
                "unit": "°C",
                "timestamp": "2024-12-22T14:30:00Z"
            }
        }


class SensorReadingResponse(BaseModel):
    """
    Response model for sensor reading queries.

    Returns a list of sensor readings with metadata.
    """
    room_name: str
    sensor_type: SensorType
    readings: list[dict] = Field(..., description="List of {timestamp, value} pairs")
    count: int = Field(..., description="Number of readings returned")
    average: Optional[float] = Field(None, description="Average value across all readings")
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    unit: SensorUnit

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_1",
                "sensor_type": "temperature",
                "readings": [
                    {"timestamp": "2024-12-22T14:00:00Z", "value": 22.5},
                    {"timestamp": "2024-12-22T14:30:00Z", "value": 23.4}
                ],
                "count": 2,
                "average": 22.95,
                "min_value": 22.5,
                "max_value": 23.4,
                "unit": "°C"
            }
        }


class SensorStatsResponse(BaseModel):
    """
    Aggregated statistics for sensor data.

    Used for dashboard and decision-making.
    """
    room_name: str
    sensor_type: SensorType
    time_range: dict = Field(..., description="Start and end timestamps")
    average: float
    min_value: float
    max_value: float
    std_deviation: Optional[float] = None
    unit: SensorUnit
    sample_count: int = Field(..., description="Number of readings used for statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "Room_1",
                "sensor_type": "co2",
                "time_range": {
                    "start": "2024-12-22T08:00:00Z",
                    "end": "2024-12-22T17:00:00Z"
                },
                "average": 650.5,
                "min_value": 420.0,
                "max_value": 890.0,
                "std_deviation": 125.3,
                "unit": "ppm",
                "sample_count": 540
            }
        }
