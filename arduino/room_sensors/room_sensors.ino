/**
 * IoT Room Sensors - Arduino Firmware
 *
 * Reads environmental sensors and publishes data via MQTT.
 * See config.h for configuration options.
 * See calibration.h for sensor conversion formulas.
 */

#include <SPI.h>
#include <Ethernet2.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "rgb_lcd.h"

#include "config.h"
#include "calibration.h"

// Ethernet and MQTT clients
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

// DHT sensor
DHT dht(DHT_PIN, DHT_TYPE);

// LCD display
rgb_lcd lcd;

// Timing variables
unsigned long lastPublishTime = 0;
unsigned long lastSensorReadTime = 0;
unsigned long lastLcdUpdateTime = 0;
unsigned long startupTime = 0;

// Sensor readings (smoothed)
float temperature = 0;
float humidity = 0;
float soundLevel = 0;
float lightIntensity = 0;
float airQuality = -1;

// Smoothing buffers
float tempBuffer[SMOOTHING_SAMPLES] = {0};
float humBuffer[SMOOTHING_SAMPLES] = {0};
float soundBuffer[SMOOTHING_SAMPLES] = {0};
float lightBuffer[SMOOTHING_SAMPLES] = {0};
float aqBuffer[SMOOTHING_SAMPLES] = {0};
int tempIdx = 0, humIdx = 0, soundIdx = 0, lightIdx = 0, aqIdx = 0;

// Air quality sensor warm-up tracking
bool airQualityWarmedUp = false;

void setup() {
    // Initialize serial for debugging
    if (DEBUG_ENABLED) {
        Serial.begin(SERIAL_BAUD);
        while (!Serial) { ; }
        DEBUG_PRINTLN("IoT Room Sensors starting...");
    }

    // Initialize LED pins
    pinMode(LED_GREEN_PIN, OUTPUT);
    digitalWrite(LED_GREEN_PIN, LOW);

    // Initialize LCD
    lcd.begin(16, 2);
    lcd.setRGB(0, 128, 255);
    lcd.print("IoT Room Sensor");
    lcd.setCursor(0, 1);
    lcd.print("Initializing...");

    // Initialize DHT sensor
    dht.begin();

    // Initialize Ethernet
    initEthernet();

    // Configure MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

    // Record startup time for warm-up tracking
    startupTime = millis();

    DEBUG_PRINTLN("Setup complete");
    lcd.clear();
    lcd.print("Setup complete");
    delay(1000);
}

void initEthernet() {
    DEBUG_PRINTLN("Initializing Ethernet...");
    lcd.clear();
    lcd.print("Init Ethernet...");

    if (USE_DHCP) {
        DEBUG_PRINTLN("Using DHCP...");
        if (Ethernet.begin(MAC_ADDRESS) == 0) {
            DEBUG_PRINTLN("DHCP failed, using static IP");
            Ethernet.begin(MAC_ADDRESS, STATIC_IP, DNS_SERVER, GATEWAY, SUBNET);
        }
    } else {
        Ethernet.begin(MAC_ADDRESS, STATIC_IP, DNS_SERVER, GATEWAY, SUBNET);
    }

    delay(1000);

    DEBUG_PRINT("IP: ");
    DEBUG_PRINTLN(Ethernet.localIP());

    lcd.clear();
    lcd.print("IP:");
    lcd.print(Ethernet.localIP());
}

void connectMQTT() {
    int retries = 0;

    while (!mqttClient.connected() && retries < MQTT_MAX_RETRIES) {
        DEBUG_PRINT("Connecting to MQTT...");
        lcd.clear();
        lcd.print("MQTT connect...");

        if (mqttClient.connect(MQTT_CLIENT_ID)) {
            DEBUG_PRINTLN("connected");
            lcd.setCursor(0, 1);
            lcd.print("Connected!");

            // Publish online status
            StaticJsonDocument<64> statusDoc;
            statusDoc["status"] = "online";
            statusDoc["room"] = ROOM_NAME;
            char statusBuffer[64];
            serializeJson(statusDoc, statusBuffer);
            mqttClient.publish(MQTT_TOPIC_STATUS, statusBuffer, true);

            digitalWrite(LED_GREEN_PIN, HIGH);
            delay(500);
        } else {
            DEBUG_PRINT("failed, rc=");
            DEBUG_PRINTLN(mqttClient.state());

            lcd.setCursor(0, 1);
            lcd.print("Failed, retry...");

            digitalWrite(LED_GREEN_PIN, LOW);
            delay(MQTT_RECONNECT_DELAY_MS);
            retries++;
        }
    }
}

void readSensors() {
    // Read DHT sensor
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (!isnan(t)) {
        temperature = smoothReading(tempBuffer, &tempIdx, t);
    }
    if (!isnan(h)) {
        humidity = smoothReading(humBuffer, &humIdx, h);
    }

    // Read analog sensors
    int soundRaw = analogRead(SOUND_PIN);
    int lightRaw = analogRead(LIGHT_PIN);
    int aqRaw = analogRead(AIR_QUALITY_PIN);

    // Convert and smooth readings
    soundLevel = smoothReading(soundBuffer, &soundIdx, convertToDecibels(soundRaw));
    lightIntensity = smoothReading(lightBuffer, &lightIdx, convertToLux(lightRaw));

    // Check if air quality sensor is warmed up
    if (!airQualityWarmedUp && (millis() - startupTime) >= AIR_QUALITY_WARMUP_MS) {
        airQualityWarmedUp = true;
        DEBUG_PRINTLN("Air quality sensor warmed up");
    }

    airQuality = convertToAQI(aqRaw, airQualityWarmedUp);
    if (airQualityWarmedUp) {
        airQuality = smoothReading(aqBuffer, &aqIdx, airQuality);
    }

    DEBUG_PRINT("T:");
    DEBUG_PRINT(temperature);
    DEBUG_PRINT(" H:");
    DEBUG_PRINT(humidity);
    DEBUG_PRINT(" S:");
    DEBUG_PRINT(soundLevel);
    DEBUG_PRINT(" L:");
    DEBUG_PRINT(lightIntensity);
    DEBUG_PRINT(" AQ:");
    DEBUG_PRINTLN(airQuality);
}

void publishSensorData() {
    StaticJsonDocument<256> doc;

    doc["temperature"] = round(temperature * 10) / 10.0;
    doc["humidity"] = round(humidity);
    doc["sound"] = round(soundLevel);
    doc["light_intensity"] = round(lightIntensity);

    if (airQualityWarmedUp && airQuality >= 0) {
        doc["air_quality"] = round(airQuality);
    }

    char buffer[256];
    serializeJson(doc, buffer);

    if (mqttClient.publish(MQTT_TOPIC_SENSORS, buffer)) {
        DEBUG_PRINT("Published: ");
        DEBUG_PRINTLN(buffer);
    } else {
        DEBUG_PRINTLN("Publish failed");
    }
}

void updateLCD() {
    lcd.clear();

    // Line 1: Temperature and Humidity
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print("C ");
    lcd.print("H:");
    lcd.print((int)humidity);
    lcd.print("%");

    // Line 2: Air Quality and Sound
    lcd.setCursor(0, 1);
    lcd.print("AQ:");
    if (airQualityWarmedUp && airQuality >= 0) {
        lcd.print((int)airQuality);
    } else {
        lcd.print("--");
    }
    lcd.print(" S:");
    lcd.print((int)soundLevel);
    lcd.print("dB");

    // Set LCD color based on air quality
    if (!airQualityWarmedUp) {
        lcd.setRGB(128, 128, 0);  // Yellow during warmup
    } else if (airQuality <= AQI_GOOD) {
        lcd.setRGB(0, 255, 0);    // Green
    } else if (airQuality <= AQI_MODERATE) {
        lcd.setRGB(255, 255, 0);  // Yellow
    } else if (airQuality <= AQI_UNHEALTHY_SENSITIVE) {
        lcd.setRGB(255, 128, 0);  // Orange
    } else {
        lcd.setRGB(255, 0, 0);    // Red
    }
}

void updateLEDs() {
    if (!airQualityWarmedUp) {
        // Blink during warmup
        digitalWrite(LED_GREEN_PIN, (millis() / LED_BLINK_INTERVAL_MS) % 2);
    } else if (airQuality <= AQI_GOOD) {
        digitalWrite(LED_GREEN_PIN, HIGH);
    } else if (airQuality <= AQI_MODERATE) {
        digitalWrite(LED_GREEN_PIN, (millis() / LED_BLINK_INTERVAL_MS) % 2);
    } else {
        digitalWrite(LED_GREEN_PIN, LOW);
    }
}

void loop() {
    unsigned long currentTime = millis();

    // Maintain MQTT connection
    if (!mqttClient.connected()) {
        connectMQTT();
    }
    mqttClient.loop();

    // Read sensors at configured interval
    if (currentTime - lastSensorReadTime >= SENSOR_READ_INTERVAL_MS) {
        readSensors();
        lastSensorReadTime = currentTime;
    }

    // Publish at configured interval
    if (currentTime - lastPublishTime >= PUBLISH_INTERVAL_MS) {
        publishSensorData();
        lastPublishTime = currentTime;
    }

    // Update LCD at configured interval
    if (currentTime - lastLcdUpdateTime >= LCD_UPDATE_INTERVAL_MS) {
        updateLCD();
        updateLEDs();
        lastLcdUpdateTime = currentTime;
    }

    // Maintain Ethernet connection
    Ethernet.maintain();
}
