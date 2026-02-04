"""
Pytest configuration and fixtures for testing.
"""
import asyncio
from datetime import datetime, timedelta

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient

from app.main import app
from app.database import db
from app.config import settings


@pytest_asyncio.fixture
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """Set up test database connection."""
    test_db_name = "iot_room_selection_test"
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[test_db_name]

    yield database

    await client.drop_database(test_db_name)
    client.close()




@pytest_asyncio.fixture(autouse=True)
async def setup_test_data(test_db):
    """
    Populate test database with sample data before each test.

    This fixture runs automatically before each test.
    """
    # Clear existing data
    await test_db.sensor_readings.delete_many({})
    await test_db.rooms.delete_many({})
    await test_db.calendar_events.delete_many({})

    # Insert test rooms
    await test_db.rooms.insert_many([
        {
            "name": "Room_1",
            "facilities": {
                "videoprojector": True,
                "seating_capacity": 62,
                "computers": 20
            },
            "building": "Building A",
            "floor": 2
        },
        {
            "name": "Room_2",
            "facilities": {
                "videoprojector": True,
                "seating_capacity": 23,
                "computers": 20,
                "robots_for_training": 10
            }
        },
        {
            "name": "Room_3",
            "facilities": {
                "videoprojector": True,
                "seating_capacity": 30,
                "computers": 10
            }
        }
    ])

    # Insert test sensor readings
    base_time = datetime.utcnow() - timedelta(hours=2)
    sensor_readings = []

    for i in range(10):
        timestamp = base_time + timedelta(minutes=i * 10)
        sensor_readings.extend([
            {
                "room_name": "Room_1",
                "sensor_type": "temperature",
                "value": 20.0 + i * 0.5,
                "unit": "°C",
                "timestamp": timestamp
            },
            {
                "room_name": "Room_1",
                "sensor_type": "co2",
                "value": 600.0 + i * 10,
                "unit": "ppm",
                "timestamp": timestamp
            },
            {
                "room_name": "Room_1",
                "sensor_type": "humidity",
                "value": 40.0 + i,
                "unit": "%",
                "timestamp": timestamp
            }
        ])

    await test_db.sensor_readings.insert_many(sensor_readings)

    # Insert test calendar events
    now = datetime.utcnow()
    await test_db.calendar_events.insert_many([
        {
            "room_name": "Room_1",
            "event_id": "test_event_1",
            "title": "CS101 Lecture",
            "start_time": now + timedelta(hours=1),
            "end_time": now + timedelta(hours=3),
            "status": "confirmed",
            "organizer": "prof.smith@uni.lu"
        },
        {
            "room_name": "Room_2",
            "event_id": "test_event_2",
            "title": "Math Seminar",
            "start_time": now + timedelta(hours=2),
            "end_time": now + timedelta(hours=4),
            "status": "confirmed",
            "organizer": "prof.jones@uni.lu"
        }
    ])

    yield

    # Cleanup after test
    await test_db.sensor_readings.delete_many({})
    await test_db.rooms.delete_many({})
    await test_db.calendar_events.delete_many({})


@pytest_asyncio.fixture
async def client(test_db):
    """Create an async HTTP client for testing."""
    # Override the database with test database
    db.database = test_db
    db.client = test_db.client

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac






