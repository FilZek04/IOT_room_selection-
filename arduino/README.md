# Arduino Room Sensors

Arduino firmware for the IoT Room Selection system. Reads environmental sensors and publishes data via MQTT to the Raspberry Pi backend.

## Hardware Requirements

### Core Components
- **Arduino Uno R3** (or compatible)
- **Ethernet Shield 2** (W5500 chipset) - stacked on Arduino
- **Grove Base Shield v2** - stacked on Ethernet Shield

### Sensors (Grove)
| Sensor | Connection | Measures |
|--------|------------|----------|
| Temp & Humidity Pro (DHT22) | D2 | Temperature (°C), Humidity (%) |
| Sound Sensor v1.6 | A0 | Sound level (dB) |
| Light Sensor v1.2 | A1 | Light intensity (lux) |
| Air Quality Sensor v1.3 | A3 | Air Quality Index (AQI) |
| LCD RGB Backlight | I2C | Display output |

### Indicators
- Green LED on D4

## Wiring Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ARDUINO UNO R3                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ETHERNET SHIELD 2                      │    │
│  │  ┌───────────────────────────────────────────────┐  │    │
│  │  │            GROVE BASE SHIELD v2               │  │    │
│  │  │                                               │  │    │
│  │  │  [D2]  ← Temp&Humidity (white 4-pin cable)    │  │    │
│  │  │  [D4]  ← Green LED                            │  │    │
│  │  │                                               │  │    │
│  │  │                                               │  │    │
│  │  │  [A0]  ← Sound Sensor (yellow 4-pin cable)    │  │    │
│  │  │  [A1]  ← Light Sensor (yellow 4-pin cable)    │  │    │
│  │  │  [A3]  ← Air Quality (yellow 4-pin cable)     │  │    │
│  │  │                                               │  │    │
│  │  │  [I2C] ← LCD RGB Backlight (4-pin cable)      │  │    │
│  │  │                                               │  │    │
│  │  └───────────────────────────────────────────────┘  │    │
│  │                                                     │    │
│  │  [RJ45] ─────→ Router/Switch (same network as Pi)   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [USB] ─────→ Computer (for programming/power)              │
│  [DC Jack] ─→ 9V power supply (alternative)                 │
└─────────────────────────────────────────────────────────────┘
```

## Software Setup

### 1. Install Arduino IDE

Download from [arduino.cc](https://www.arduino.cc/en/software).

### 2. Install Required Libraries

Open Arduino IDE → Tools → Manage Libraries, then install:

| Library | Author | Version |
|---------|--------|---------|
| Ethernet2 | Arduino | 1.0.4+ |
| PubSubClient | Nick O'Leary | 2.8+ |
| DHT sensor library | Adafruit | 1.4.4+ |
| ArduinoJson | Benoit Blanchon | 6.x |
| Grove - LCD RGB Backlight | Seeed Studio | 1.0.0+ |

**Note:** Also install "Adafruit Unified Sensor" when prompted (dependency for DHT).

### 3. Configure the Firmware

Edit `config.h` before uploading:

```cpp
// Set your room name (must match MongoDB)
#define ROOM_NAME "Room_1"

// Set your Raspberry Pi's IP address
#define MQTT_BROKER "192.168.1.50"

// If using static IP, configure network settings
#define USE_DHCP true
static byte STATIC_IP[] = {192, 168, 1, 100};
```

### 4. Upload to Arduino

1. Connect Arduino via USB
2. Select board: Tools → Board → Arduino Uno
3. Select port: Tools → Port → (your Arduino port)
4. Click Upload (→ button)

## LED Indicator States

| Air Quality (AQI) | Green LED | Red LED | Meaning |
|-------------------|-----------|---------|---------|
| Warming up | Alternating | Alternating | Sensor needs 2min to stabilize |
| 0-50 | Solid ON | OFF | Good air quality |
| 51-100 | Blinking | OFF | Moderate |
| 101-150 | OFF | Blinking | Unhealthy for sensitive groups |
| 151+ | OFF | Solid ON | Unhealthy |

## LCD Display

```
┌────────────────┐
│T:23.4C  H:55%  │  ← Temperature & Humidity
│AQ:45  S:42dB   │  ← Air Quality & Sound
└────────────────┘
```

## MQTT Topics

The Arduino publishes to:

```
iot/{ROOM_NAME}/sensors
```

Example payload:
```json
{
  "temperature": 23.4,
  "humidity": 55,
  "sound": 42,
  "light_intensity": 450,
  "air_quality": 45
}
```

Status topic (retained):
```
iot/{ROOM_NAME}/status
```

## Sensor Calibration

The sensors use approximate conversion formulas in `calibration.h`. For more accurate readings:

### Sound Sensor
1. Use a phone app or reference meter to measure actual dB
2. Note the analog reading at that level
3. Adjust `SOUND_OFFSET` and `SOUND_SCALE` in `calibration.h`

### Light Sensor
1. Use a lux meter under known lighting (e.g., 500 lux office)
2. Note the analog reading
3. Adjust `LUX_CONSTANT` and `LUX_EXPONENT` in `calibration.h`

### Air Quality Sensor
1. Take the sensor outdoors in fresh air for baseline
2. Reading should be < 100 (fresh air)
3. Adjust `AQ_FRESH_AIR` threshold if needed

## Troubleshooting

### No network connection
- Check Ethernet cable is connected
- Verify DHCP is working on your network
- Try static IP configuration
- Check MAC address is unique if multiple Arduinos

### MQTT not connecting
- Verify Mosquitto broker is running on Pi: `sudo systemctl status mosquitto`
- Check Pi IP address matches `MQTT_BROKER` in config
- Test broker: `mosquitto_pub -h <pi-ip> -t test -m "hello"`
- Check firewall allows port 1883


### Air quality shows "--"
- Sensor needs 2 minutes warm-up time after power on


### Readings seem wrong
- Check calibration constants in `calibration.h`
- Sound/light are approximations without reference calibration
- Temperature accuracy depends on DHT sensor quality

## Power Options

1. **USB Power** - Connect to computer or 5V USB adapter (500mA+)
2. **DC Jack** - Use 9V 1A power supply
3. **PoE** - With PoE-enabled Ethernet Shield

## Network Requirements

- Same network/VLAN as Raspberry Pi
- DHCP enabled (or static IP configured)
- UDP port 1883 open (MQTT)
- Recommended: Reserved/static DHCP lease for consistent IP

## File Structure

```
arduino/room_sensors/
├── room_sensors.ino    # Main Arduino sketch
├── config.h            # Configuration (edit before upload)
├── calibration.h       # Sensor conversion formulas
└── README.md           # This file
```

## Known Limitations

- **No CO2 sensor** - Air quality sensor detects VOCs, not CO2 specifically
- **Sound calibration** - dB readings are approximate without reference meter
- **Light calibration** - Lux conversion is sensor-specific approximation
- **Air quality warm-up** - Sensor needs ~2 minutes to stabilize after power-up
- **Single room** - Each Arduino handles one room; deploy multiple for multiple rooms
