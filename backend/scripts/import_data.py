#!/usr/bin/env python3
"""Import mock sensor data and room facilities from JSON files into MongoDB."""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "project info&data" / "Project_sensor_data"

SENSOR_FILES = {
    "temperature": DATA_DIR / "temperature_sensor_data.json",
    "co2": DATA_DIR / "co2_sensor_data.json",
    "humidity": DATA_DIR / "humidity_sensor_data.json",
    "sound": DATA_DIR / "sound_sensor_data.json",
    "voc": DATA_DIR / "voc_sensor_data.json",
    "light_intensity": DATA_DIR / "LightIntensity_sensor_data.json",
    "air_quality": DATA_DIR / "air_quality_sensor_data.json",
}

FACILITIES_FILE = DATA_DIR / "room_facilities_data.json"

SENSOR_UNITS = {
    "temperature": "°C",
    "co2": "ppm",
    "humidity": "%",
    "sound": "dB",
    "voc": "ppb",
    "light_intensity": "lux",
    "air_quality": "AQI",
}


async def import_sensor_data(db, sensor_type: str, file_path: Path):
    """Import sensor data from JSON file."""
    print(f"\nImporting {sensor_type} data from {file_path.name}...")

    if not file_path.exists():
        print(f"  Warning: File not found: {file_path}")
        return 0

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        collection = db.sensor_readings
        documents = []
        batch_size = 1000

        for room_data in data.get("rooms", []):
            room_name = room_data["name"]

            values_key = f"{sensor_type}_values"
            if sensor_type == "light_intensity":
                values_key = "light_intensity_values"
            elif sensor_type == "co2":
                values_key = "co2_values"
            elif sensor_type == "sound":
                values_key = "sound_values"
            elif sensor_type == "air_quality":
                values_key = "air_quality_values"

            sensor_values = room_data.get(values_key, [])

            for reading in sensor_values:
                timestamp = datetime.fromisoformat(reading["timestamp"].replace("Z", "+00:00"))
                value = None

                if sensor_type == "temperature":
                    value = reading.get("temperature")
                elif sensor_type == "co2":
                    value = reading.get("co2_level")
                elif sensor_type == "humidity":
                    value = reading.get("humidity")
                elif sensor_type == "sound":
                    value = reading.get("sound_level")
                elif sensor_type == "voc":
                    value = reading.get("voc_level")
                elif sensor_type == "light_intensity":
                    value = reading.get("light_intensity")
                elif sensor_type == "air_quality":
                    pm25 = reading.get("PM2.5")
                    pm10 = reading.get("PM10")
                    if pm25 is not None and pm10 is not None:
                        value = (pm25 + pm10) / 2
                    elif pm25 is not None:
                        value = pm25
                    elif pm10 is not None:
                        value = pm10
                    else:
                        value = None

                if value is None:
                    continue

                document = {
                    "room_name": room_name,
                    "sensor_type": sensor_type,
                    "value": float(value),
                    "unit": SENSOR_UNITS[sensor_type],
                    "timestamp": timestamp,
                    "created_at": datetime.utcnow()
                }

                documents.append(document)

                if len(documents) >= batch_size:
                    await collection.insert_many(documents)
                    print(f"  Inserted {len(documents)} readings...")
                    documents = []

        if documents:
            await collection.insert_many(documents)

        total = await collection.count_documents({"sensor_type": sensor_type})
        print(f"  Total {sensor_type} readings in DB: {total:,}")
        return total

    except Exception as e:
        print(f"  Error importing {sensor_type}: {e}")
        return 0


async def import_room_facilities(db, file_path: Path):
    """Import room facilities data from JSON file."""
    print(f"\nImporting room facilities from {file_path.name}...")

    if not file_path.exists():
        print(f"  Warning: File not found: {file_path}")
        return 0

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        collection = db.rooms
        documents = []

        for room_data in data.get("rooms", []):
            document = {
                "name": room_data["name"],
                "facilities": room_data["facilities"],
                "updated_at": datetime.utcnow()
            }
            documents.append(document)

        if documents:
            for doc in documents:
                await collection.update_one(
                    {"name": doc["name"]},
                    {"$set": doc},
                    upsert=True
                )

        total = await collection.count_documents({})
        print(f"  Total rooms in DB: {total}")
        return total

    except Exception as e:
        print(f"  Error importing facilities: {e}")
        return 0


async def create_indexes(db):
    """Create database indexes."""
    print("\nCreating database indexes...")

    try:
        await db.sensor_readings.create_index(
            [("room_name", 1), ("sensor_type", 1), ("timestamp", -1)],
            name="room_sensor_time_idx"
        )
        await db.sensor_readings.create_index(
            [("sensor_type", 1), ("timestamp", -1)],
            name="sensor_time_idx"
        )

        await db.rooms.create_index(
            [("name", 1)],
            unique=True,
            name="room_name_unique_idx"
        )

        print("  Indexes created successfully")
    except Exception as e:
        print(f"  Index creation warning: {e}")


async def show_statistics(db):
    """Show import statistics."""
    print("\n" + "="*60)
    print("Import Statistics")
    print("="*60)

    total_sensor_readings = await db.sensor_readings.count_documents({})
    print(f"Total sensor readings: {total_sensor_readings:,}")

    for sensor_type in SENSOR_FILES.keys():
        count = await db.sensor_readings.count_documents({"sensor_type": sensor_type})
        print(f"  - {sensor_type}: {count:,}")

    total_rooms = await db.rooms.count_documents({})
    print(f"\nTotal rooms: {total_rooms}")

    pipeline = [
        {
            "$group": {
                "_id": None,
                "min_timestamp": {"$min": "$timestamp"},
                "max_timestamp": {"$max": "$timestamp"}
            }
        }
    ]
    result = await db.sensor_readings.aggregate(pipeline).to_list(1)
    if result:
        print(f"\nData time range:")
        print(f"  From: {result[0]['min_timestamp']}")
        print(f"  To:   {result[0]['max_timestamp']}")

    print("="*60)


async def main():
    """Main import function."""
    print("="*60)
    print("IoT Room Selection - Data Import Script")
    print("="*60)
    print(f"MongoDB URL: {settings.MONGODB_URL}")
    print(f"Database: {settings.MONGODB_DB_NAME}")

    print("\nConnecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        await client.admin.command('ping')
        print("  Connected successfully")
    except Exception as e:
        print(f"  Connection failed: {e}")
        return

    try:
        print("\nClearing existing data...")
        await db.sensor_readings.delete_many({})
        await db.rooms.delete_many({})
        print("  Existing data cleared")

        await import_room_facilities(db, FACILITIES_FILE)

        total_imported = 0
        for sensor_type, file_path in SENSOR_FILES.items():
            count = await import_sensor_data(db, sensor_type, file_path)
            total_imported += count

        await create_indexes(db)
        await show_statistics(db)

        print("\nImport completed successfully!")
        print("\nNext steps:")
        print("  1. Start the API: uvicorn app.main:app --reload")
        print("  2. View docs at: http://localhost:8000/docs")
        print("  3. Run tests: pytest")

    except Exception as e:
        print(f"\nImport failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
