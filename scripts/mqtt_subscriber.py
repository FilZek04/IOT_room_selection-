#!/usr/bin/env python3
"""
MQTT Subscriber for IoT Room Selection System

Subscribes to sensor data from Arduino nodes and stores in MongoDB.
Runs as a systemd service on Raspberry Pi.
"""

import os
import sys
import json
import signal
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from pymongo import MongoClient

# Configuration from environment
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "iot_room_selection")

# MQTT topics
TOPIC_SENSORS = "iot/+/sensors"
TOPIC_OCCUPANCY = "iot/+/occupancy"
TOPIC_STATUS = "iot/+/status"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global MongoDB client
mongo_client = None
db = None
running = True


def get_room_name_from_topic(topic: str) -> str:
    """Extract room name from MQTT topic like 'iot/Room_1/sensors'"""
    parts = topic.split("/")
    if len(parts) >= 2:
        return parts[1]
    return "unknown"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(TOPIC_SENSORS)
        client.subscribe(TOPIC_OCCUPANCY)
        client.subscribe(TOPIC_STATUS)
        logger.info(f"Subscribed to: {TOPIC_SENSORS}, {TOPIC_OCCUPANCY}, {TOPIC_STATUS}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker (rc={rc})")


def on_message(client, userdata, msg):
    """Callback when message received from MQTT broker"""
    try:
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        room_name = get_room_name_from_topic(topic)

        logger.debug(f"Received on {topic}: {payload}")

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON from {topic}: {e}")
            return

        timestamp = datetime.now(timezone.utc)

        if topic.endswith("/sensors"):
            store_sensor_readings(room_name, data, timestamp)
        elif topic.endswith("/occupancy"):
            store_occupancy_reading(room_name, data, timestamp)
        elif topic.endswith("/status"):
            logger.info(f"Status from {room_name}: {data}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")


def store_sensor_readings(room_name: str, data: dict, timestamp: datetime):
    """Store individual sensor readings in MongoDB"""
    collection = db["sensor_readings"]

    sensor_mappings = {
        "temperature": ("temperature", "celsius"),
        "humidity": ("humidity", "percent"),
        "sound": ("noise", "dB"),
        "light_intensity": ("light", "lux"),
        "air_quality": ("air_quality", "AQI"),
    }

    documents = []
    for field, (sensor_type, unit) in sensor_mappings.items():
        if field in data:
            doc = {
                "room_name": room_name,
                "sensor_type": sensor_type,
                "value": float(data[field]),
                "unit": unit,
                "timestamp": timestamp,
            }
            documents.append(doc)

    if documents:
        collection.insert_many(documents)
        logger.info(f"Stored {len(documents)} readings from {room_name}")


def store_occupancy_reading(room_name: str, data: dict, timestamp: datetime):
    """Store occupancy count in MongoDB"""
    collection = db["sensor_readings"]

    if isinstance(data, dict):
        count = data.get("count", data.get("occupancy", 0))
    else:
        count = int(data)

    doc = {
        "room_name": room_name,
        "sensor_type": "occupancy",
        "value": count,
        "unit": "count",
        "timestamp": timestamp,
    }

    collection.insert_one(doc)
    logger.info(f"Stored occupancy reading from {room_name}: {count}")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


def main():
    global mongo_client, db, running

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        mongo_client = MongoClient(MONGODB_URL)
        db = mongo_client[MONGODB_DB_NAME]
        mongo_client.admin.command("ping")
        logger.info(f"Connected to MongoDB at {MONGODB_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    client.loop_start()

    logger.info("MQTT Subscriber running. Press Ctrl+C to stop.")
    try:
        while running:
            signal.pause()
    except AttributeError:
        import time
        while running:
            time.sleep(1)

    logger.info("Shutting down...")
    client.loop_stop()
    client.disconnect()
    if mongo_client:
        mongo_client.close()
    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
