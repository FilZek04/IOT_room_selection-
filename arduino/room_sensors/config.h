/**
 * Configuration for IoT Room Sensors
 *
 * This file contains all configurable parameters for the Arduino
 * room sensor system including network settings, MQTT configuration,
 * pin assignments, and timing.
 *
 * Modify these values to match your setup before uploading.
 */

#ifndef CONFIG_H
#define CONFIG_H

// =============================================================================
// ROOM CONFIGURATION
// =============================================================================

// Room identifier - must match MongoDB room_name
#define ROOM_NAME "Room_1"

// =============================================================================
// NETWORK CONFIGURATION
// =============================================================================

// Use DHCP for automatic IP assignment (recommended)
#define USE_DHCP false

// Static IP configuration (used if USE_DHCP is false)
// Modify these to match your network
static byte STATIC_IP[] = {192, 168, 1, 100};
static byte GATEWAY[] = {192, 168, 1, 1};
static byte SUBNET[] = {255, 255, 255, 0};
static byte DNS_SERVER[] = {192, 168, 1, 1};

// MAC address for Ethernet Shield
// Change last bytes to make unique if you have multiple Arduinos
static byte MAC_ADDRESS[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0x01};

// =============================================================================
// MQTT CONFIGURATION
// =============================================================================

// MQTT Broker (Raspberry Pi running Mosquitto)
// Use IP address or hostname
#define MQTT_BROKER "192.168.1.1"  // Raspberry Pi eth0 IP
// #define MQTT_BROKER "raspberrypi.local"  // Or use mDNS hostname

#define MQTT_PORT 1883

// MQTT Client ID - should be unique per device
#define MQTT_CLIENT_ID "arduino_room1"

// MQTT Topics
#define MQTT_TOPIC_SENSORS "iot/" ROOM_NAME "/sensors"
#define MQTT_TOPIC_STATUS "iot/" ROOM_NAME "/status"

// MQTT reconnection settings
#define MQTT_RECONNECT_DELAY_MS 5000
#define MQTT_MAX_RETRIES 10

// =============================================================================
// SENSOR PIN ASSIGNMENTS
// =============================================================================

// Digital pins
#define DHT_PIN 2               // Grove Temp & Humidity sensor (D2)
#define LED_GREEN_PIN 4         // Green LED indicator (D4)
#define LED_RED_PIN 5           // Red LED indicator (D5)

// Analog pins
#define SOUND_PIN A0            // Grove Sound sensor
#define LIGHT_PIN A1            // Grove Light sensor
#define AIR_QUALITY_PIN A3      // Grove Air Quality sensor (A2 is broken)

// I2C (used by LCD, no pin definition needed - uses SDA/SCL)

// =============================================================================
// DHT SENSOR CONFIGURATION
// =============================================================================

// DHT sensor type: DHT11 or DHT22
// Grove Temp&Humi Pro uses DHT22, basic version uses DHT11
// #define DHT_TYPE DHT22
#define DHT_TYPE DHT11  // Blue housing = DHT11

// =============================================================================
// TIMING CONFIGURATION
// =============================================================================

// How often to publish sensor readings (milliseconds)
#define PUBLISH_INTERVAL_MS 60000  // 60 seconds

// How often to read sensors (should be faster than publish)
#define SENSOR_READ_INTERVAL_MS 5000  // 5 seconds

// LCD update interval
#define LCD_UPDATE_INTERVAL_MS 2000  // 2 seconds

// LED blink interval for warning states
#define LED_BLINK_INTERVAL_MS 500  // 0.5 seconds

// Air quality sensor warm-up time
#define AIR_QUALITY_WARMUP_MS 120000  // 2 minutes

// =============================================================================
// SENSOR THRESHOLDS (for LED indicators)
// =============================================================================

// Air Quality Index thresholds (EPA scale)
#define AQI_GOOD 50             // Green LED solid
#define AQI_MODERATE 100        // Green LED blink
#define AQI_UNHEALTHY_SENSITIVE 150  // Red LED blink
#define AQI_UNHEALTHY 200       // Red LED solid

// =============================================================================
// DEBUG CONFIGURATION
// =============================================================================

// Enable serial debug output (disable when using UART for Vision AI)
#define DEBUG_ENABLED false

// Serial baud rate (115200 for Vision AI V2)
#define SERIAL_BAUD 115200

// Debug print macro
#if DEBUG_ENABLED
  #define DEBUG_PRINT(x) Serial.print(x)
  #define DEBUG_PRINTLN(x) Serial.println(x)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
#endif

#endif // CONFIG_H
