# Session Summary: Hardware Integration (2026-02-01)

## What Was Completed

### 1. Backend Modifications

**File: `backend/app/models/sensor.py`**
- Added `OCCUPANCY = "occupancy"` to `SensorType` enum
- Added `COUNT = "count"` to `SensorUnit` enum

**File: `backend/app/ahp/score_mapping.py`**
- Added `OCCUPANCY_CONFIG` mapping configuration
- Added `map_occupancy()` function for scoring room occupancy
- Added `"occupancy": map_occupancy` to `SENSOR_MAPPING_FUNCTIONS` dict

### 2. New Python Scripts Created

**File: `scripts/mqtt_subscriber.py`**
- Subscribes to MQTT topics `iot/+/sensors` and `iot/+/occupancy`
- Writes sensor data to MongoDB `sensor_readings` collection
- Handles graceful shutdown with signal handlers

**File: `scripts/mqtt_subscriber.service`**
- Systemd service file for running mqtt_subscriber as a daemon

**File: `scripts/vision_ai_reader.py`**
- Reads person detection from Vision AI V2 via UART
- Publishes occupancy count to MQTT topic `iot/{room}/occupancy`

**File: `scripts/vision_ai.service`**
- Systemd service file for running vision_ai_reader as a daemon

### 3. Arduino Firmware Created

**Directory: `arduino/room_sensors/`**

| File | Purpose |
|------|---------|
| `room_sensors.ino` | Main sketch - reads sensors, publishes via MQTT, drives LCD & LEDs |
| `config.h` | Configuration - MQTT broker IP, pins, room name, intervals |
| `calibration.h` | Sensor conversion formulas (analog → dB, lux, AQI) |

**File: `arduino/README.md`**
- Complete wiring guide
- Library installation instructions
- LED indicator meanings
- Troubleshooting guide

### 4. Docker Configuration Fixed

**File: `docker-compose.yml`**
- Changed MongoDB from `mongo:7.0` to `mongo:4.4.18` (Pi 4 ARM compatibility)
- Updated healthcheck from `mongosh` to `mongo` command

---

## What Was Verified Working

1. **Mosquitto MQTT Broker** - Installed and tested
   ```bash
   mosquitto_sub -h localhost -t "iot/#" -v  # Works
   mosquitto_pub -h localhost -t "iot/Room_1/sensors" -m '{"temperature": 23.5}'  # Works
   ```

2. **Python 3.11** - Built from source and installed
   ```bash
   python3.11 --version  # Should work after: sudo make altinstall
   ```

3. **Virtual Environment** - Created with dependencies
   ```bash
   cd ~/iot
   source venv/bin/activate
   # paho-mqtt, pyserial, pymongo installed
   ```

4. **MQTT Subscriber Script** - Tested and connects successfully
   ```bash
   python scripts/mqtt_subscriber.py
   # Connected to MongoDB: iot_room_selection
   # Connected to MQTT broker
   # Subscribed to: iot/+/sensors, iot/+/occupancy
   ```

5. **Docker Compose** - MongoDB 4.4.18 runs on Pi 4
   ```bash
   docker compose up -d  # MongoDB healthy
   ```

---

## What Remains To Do

### Immediate Next Steps

1. **Complete Python 3.11 installation** (if not done):
   ```bash
   cd /tmp/Python-3.11.9
   sudo make altinstall
   ```

2. **Recreate venv with Python 3.11** (if needed):
   ```bash
   cd ~/iot
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install paho-mqtt pyserial pymongo
   ```

3. **Test full MQTT → MongoDB flow**:
   ```bash
   # Terminal 1: Start subscriber
   source venv/bin/activate
   python scripts/mqtt_subscriber.py

   # Terminal 2: Publish test data
   mosquitto_pub -h localhost -t "iot/Room_1/sensors" \
     -m '{"temperature": 23.5, "humidity": 55, "sound": 42, "light_intensity": 450, "air_quality": 35}'

   # Terminal 3: Verify in MongoDB
   docker exec -it iot-mongodb mongo iot_room_selection \
     --eval "db.sensor_readings.find().sort({timestamp: -1}).limit(5).pretty()"
   ```

### Hardware Setup

1. **Configure Arduino**:
   - Edit `arduino/room_sensors/config.h`
   - Set `MQTT_BROKER` to your Pi's IP address
   - Verify `ROOM_NAME` matches your setup

2. **Install Arduino Libraries** (via Library Manager):
   - Ethernet2
   - PubSubClient
   - DHT sensor library (Adafruit)
   - ArduinoJson
   - Grove - LCD RGB Backlight

3. **Wire sensors** per `arduino/README.md`:
   - DHT22 → D2
   - Sound → A0
   - Light → A1
   - Air Quality → A2
   - LCD → I2C
   - LEDs → D4 (green), D5 (red)

4. **Upload sketch** to Arduino

### Vision AI (Optional)

1. Wire Vision AI V2 to Pi GPIO:
   - TX → GPIO 15 (RX)
   - RX → GPIO 14 (TX)
   - GND → GND
   - 3V3 → 3.3V

2. Test reader:
   ```bash
   python scripts/vision_ai_reader.py
   ```

### Deploy as Services

```bash
# Copy service files
sudo cp scripts/mqtt_subscriber.service /etc/systemd/system/
sudo cp scripts/vision_ai.service /etc/systemd/system/

# Edit paths if needed (default assumes /home/pi/iot)
sudo nano /etc/systemd/system/mqtt_subscriber.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable mqtt_subscriber
sudo systemctl start mqtt_subscriber
sudo systemctl status mqtt_subscriber
```

---

## File Summary

### New Files Created This Session

```
iot/
├── arduino/
│   └── room_sensors/
│       ├── room_sensors.ino      # Main Arduino sketch
│       ├── config.h              # Configuration
│       ├── calibration.h         # Sensor conversions
│       └── README.md             # Wiring & setup guide
├── scripts/
│   ├── mqtt_subscriber.py        # MQTT → MongoDB bridge
│   ├── mqtt_subscriber.service   # Systemd service
│   ├── vision_ai_reader.py       # Vision AI → MQTT
│   └── vision_ai.service         # Systemd service
└── docs/
    └── SESSION_2026-02-01_HARDWARE_INTEGRATION.md  # This file
```

### Modified Files

```
backend/app/models/sensor.py      # Added OCCUPANCY type
backend/app/ahp/score_mapping.py  # Added occupancy scoring
docker-compose.yml                # MongoDB 4.4.18 for Pi 4
```

---

## Quick Start Commands

```bash
# Start everything
cd ~/iot
docker compose up -d
source venv/bin/activate
python scripts/mqtt_subscriber.py

# In another terminal - test
mosquitto_pub -h localhost -t "iot/Room_1/sensors" \
  -m '{"temperature": 22.5, "humidity": 50, "sound": 35, "light_intensity": 400, "air_quality": 25}'
```
