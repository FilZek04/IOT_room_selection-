#!/usr/bin/env python3
"""
Vision AI Reader for IoT Room Selection System

Reads person count from Vision AI V2 module via UART and publishes to MQTT.
Runs as a systemd service on Raspberry Pi.
"""

import os
import sys
import json
import signal
import logging
import time

import serial
import paho.mqtt.client as mqtt

# Configuration from environment
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
ROOM_NAME = os.getenv("ROOM_NAME", "Room_1")
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyAMA0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "115200"))

# MQTT topic for occupancy
MQTT_TOPIC = f"iot/{ROOM_NAME}/occupancy"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

running = True
mqtt_client = None


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker (rc={rc})")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


def publish_occupancy(count: int):
    """Publish occupancy count to MQTT"""
    if mqtt_client and mqtt_client.is_connected():
        payload = json.dumps({"count": count})
        mqtt_client.publish(MQTT_TOPIC, payload)
        logger.debug(f"Published occupancy: {count}")


def read_vision_ai(ser: serial.Serial) -> int:
    """
    Read person count from Vision AI V2 module.

    The Vision AI sends person detection results over UART.
    Format depends on firmware - adjust parsing as needed.
    """
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()

            # Try parsing as JSON first
            try:
                data = json.loads(line)
                if "count" in data:
                    return int(data["count"])
                if "people" in data:
                    return int(data["people"])
                if "persons" in data:
                    return int(data["persons"])
            except json.JSONDecodeError:
                pass

            # Try parsing as plain integer
            try:
                return int(line)
            except ValueError:
                pass

            # Try parsing "count: N" format
            if ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        return int(parts[1].strip())
                    except ValueError:
                        pass

            logger.debug(f"Could not parse Vision AI output: {line}")

    except Exception as e:
        logger.error(f"Error reading from Vision AI: {e}")

    return -1


def main():
    global mqtt_client, running

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Setup MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    # Setup serial connection
    ser = None
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUD,
            timeout=1,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        logger.info(f"Opened serial port {SERIAL_PORT} at {SERIAL_BAUD} baud")
    except Exception as e:
        logger.error(f"Failed to open serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

    logger.info(f"Vision AI Reader running for {ROOM_NAME}. Press Ctrl+C to stop.")

    last_count = -1
    last_publish_time = 0
    publish_interval = 1.0  # Publish at most every 1 second

    while running:
        try:
            count = read_vision_ai(ser)

            current_time = time.time()

            # Publish if count changed or interval elapsed
            if count >= 0 and (count != last_count or current_time - last_publish_time >= publish_interval):
                publish_occupancy(count)
                last_count = count
                last_publish_time = current_time

            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(1)

    # Cleanup
    logger.info("Shutting down...")
    if ser:
        ser.close()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
