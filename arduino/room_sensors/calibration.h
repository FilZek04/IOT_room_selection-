/**
 * Sensor Calibration for IoT Room Sensors
 *
 * This file contains conversion formulas to translate raw analog
 * readings into meaningful units (dB, lux, AQI).
 *
 * IMPORTANT: These are approximate conversions based on typical
 * Grove sensor characteristics. For accurate measurements:
 * 1. Use a reference meter to calibrate
 * 2. Adjust the constants below based on your specific sensors
 * 3. Consider environmental factors (temperature affects readings)
 */

#ifndef CALIBRATION_H
#define CALIBRATION_H

// =============================================================================
// SOUND SENSOR CALIBRATION (Grove Sound Sensor v1.6)
// =============================================================================

/**
 * Convert analog reading to approximate dB level.
 *
 * The Grove Sound Sensor outputs a voltage proportional to sound amplitude.
 * This is a simplified logarithmic conversion - not laboratory accurate.
 *
 * Calibration procedure:
 * 1. In a quiet room (~30dB), note the analog reading
 * 2. With a known sound source (e.g., phone app at 70dB), note reading
 * 3. Adjust SOUND_OFFSET and SOUND_SCALE accordingly
 *
 * @param analogValue Raw analog reading (0-1023)
 * @return Approximate sound level in dB
 */
float convertToDecibels(int analogValue) {
    // Prevent log(0)
    if (analogValue <= 0) {
        return 30.0;  // Baseline quiet room
    }

    // Convert to voltage (5V reference, 10-bit ADC)
    float voltage = analogValue * (5.0 / 1023.0);

    // Empirical conversion to dB
    // Adjust these based on calibration with reference meter
    const float SOUND_OFFSET = 30.0;   // dB at minimum reading
    const float SOUND_SCALE = 20.0;    // dB range multiplier

    // Logarithmic conversion (sound is logarithmic)
    float dB = SOUND_OFFSET + SOUND_SCALE * log10(voltage + 0.001);

    // Clamp to reasonable range
    if (dB < 30.0) dB = 30.0;
    if (dB > 100.0) dB = 100.0;

    return dB;
}

// =============================================================================
// LIGHT SENSOR CALIBRATION (Grove Light Sensor v1.2)
// =============================================================================

/**
 * Convert analog reading to approximate lux.
 *
 * The Grove Light Sensor uses a photoresistor (LDR).
 * Resistance decreases with light, creating voltage divider output.
 *
 * Calibration procedure:
 * 1. In complete darkness, note the analog reading
 * 2. Under known lighting (e.g., 500 lux office light), note reading
 * 3. Adjust the formula constants accordingly
 *
 * @param analogValue Raw analog reading (0-1023)
 * @return Approximate light intensity in lux
 */
float convertToLux(int analogValue) {
    // Prevent division by zero
    if (analogValue <= 0) {
        return 0.0;
    }

    // Convert analog value to lux using empirical formula
    // This formula is specific to the Grove Light Sensor
    // Based on logarithmic relationship between resistance and lux

    // Sensor-specific constants (adjust for your sensor)
    const float LUX_CONSTANT = 500000.0;  // Calibration constant
    const float LUX_EXPONENT = -1.4;      // Power relationship

    // Calculate lux
    float resistance = (float)(1023 - analogValue) * 10.0 / analogValue;
    float lux = LUX_CONSTANT * pow(resistance, LUX_EXPONENT);

    // Clamp to reasonable indoor range
    if (lux < 0.0) lux = 0.0;
    if (lux > 10000.0) lux = 10000.0;

    return lux;
}

/**
 * Alternative simpler lux conversion (linear approximation)
 * Use this if the logarithmic formula doesn't match your sensor
 *
 * @param analogValue Raw analog reading (0-1023)
 * @return Approximate light intensity in lux
 */
float convertToLuxLinear(int analogValue) {
    // Simple linear mapping
    // Assumes 0 analog = 0 lux, 1023 analog = 1000 lux
    // Adjust MAX_LUX based on your sensor under known lighting
    const float MAX_LUX = 1000.0;

    return (analogValue / 1023.0) * MAX_LUX;
}

// =============================================================================
// AIR QUALITY SENSOR CALIBRATION (Grove Air Quality Sensor v1.3)
// =============================================================================

// Sensor state thresholds (from Grove documentation)
#define AQ_HIGH_POLLUTION 700     // High pollution threshold
#define AQ_LOW_POLLUTION 300      // Low pollution threshold
#define AQ_FRESH_AIR 100          // Fresh air threshold

/**
 * Convert analog reading to Air Quality Index (AQI).
 *
 * The Grove Air Quality Sensor detects:
 * - Carbon monoxide (CO)
 * - Alcohol
 * - Acetone
 * - Thinner
 * - Formaldehyde
 * - Other gases
 *
 * Note: This is NOT a CO2 sensor. For CO2, you need Grove CO2 Sensor.
 *
 * Calibration procedure:
 * 1. Allow 2+ minutes warm-up time
 * 2. In clean outdoor air, note the reading (should be < 100)
 * 3. This becomes your baseline for "Fresh Air"
 *
 * @param analogValue Raw analog reading (0-1023)
 * @param isWarmedUp Whether sensor has completed warm-up period
 * @return AQI value (0-500 scale, EPA standard)
 */
float convertToAQI(int analogValue, bool isWarmedUp) {
    // During warm-up, return placeholder value
    if (!isWarmedUp) {
        return -1.0;  // Indicates sensor warming up
    }

    // Map analog reading to AQI scale
    // Lower analog = better air quality
    // AQI scale: 0-50 Good, 51-100 Moderate, 101-150 Unhealthy for Sensitive,
    //            151-200 Unhealthy, 201-300 Very Unhealthy, 301-500 Hazardous

    float aqi;

    if (analogValue < AQ_FRESH_AIR) {
        // Fresh air: AQI 0-25
        aqi = (analogValue / (float)AQ_FRESH_AIR) * 25.0;
    }
    else if (analogValue < AQ_LOW_POLLUTION) {
        // Good to Moderate: AQI 25-100
        aqi = 25.0 + ((analogValue - AQ_FRESH_AIR) /
              (float)(AQ_LOW_POLLUTION - AQ_FRESH_AIR)) * 75.0;
    }
    else if (analogValue < AQ_HIGH_POLLUTION) {
        // Moderate to Unhealthy: AQI 100-200
        aqi = 100.0 + ((analogValue - AQ_LOW_POLLUTION) /
              (float)(AQ_HIGH_POLLUTION - AQ_LOW_POLLUTION)) * 100.0;
    }
    else {
        // Unhealthy to Hazardous: AQI 200-500
        aqi = 200.0 + ((analogValue - AQ_HIGH_POLLUTION) /
              (float)(1023 - AQ_HIGH_POLLUTION)) * 300.0;
    }

    // Clamp to EPA scale
    if (aqi < 0.0) aqi = 0.0;
    if (aqi > 500.0) aqi = 500.0;

    return aqi;
}

/**
 * Get air quality status string for display
 *
 * @param aqi Air Quality Index value
 * @return Status string
 */
const char* getAQIStatus(float aqi) {
    if (aqi < 0) return "Warmup";
    if (aqi <= 50) return "Good";
    if (aqi <= 100) return "Moderate";
    if (aqi <= 150) return "Sens.Unhlth";
    if (aqi <= 200) return "Unhealthy";
    if (aqi <= 300) return "VeryUnhlth";
    return "Hazardous";
}

// =============================================================================
// TEMPERATURE/HUMIDITY ADJUSTMENTS
// =============================================================================

/**
 * Apply altitude correction to temperature if needed
 * Temperature typically decreases ~6.5°C per 1000m elevation
 *
 * @param tempC Temperature in Celsius
 * @param altitudeMeters Altitude in meters above sea level
 * @return Corrected temperature
 */
float correctTemperatureForAltitude(float tempC, int altitudeMeters) {
    // Standard lapse rate: 6.5°C per 1000m
    // This corrects to sea-level equivalent temperature
    return tempC + (altitudeMeters / 1000.0) * 6.5;
}

// =============================================================================
// AVERAGING / SMOOTHING
// =============================================================================

// Number of samples for moving average (reduces noise)
#define SMOOTHING_SAMPLES 5

/**
 * Simple moving average for smoothing sensor readings
 * Call repeatedly with new values to maintain average
 *
 * @param buffer Array to store samples (size = SMOOTHING_SAMPLES)
 * @param index Pointer to current index (0 to SMOOTHING_SAMPLES-1)
 * @param newValue New reading to add
 * @return Smoothed average value
 */
float smoothReading(float* buffer, int* index, float newValue) {
    // Add new value to buffer
    buffer[*index] = newValue;

    // Increment index with wrap-around
    *index = (*index + 1) % SMOOTHING_SAMPLES;

    // Calculate average
    float sum = 0;
    for (int i = 0; i < SMOOTHING_SAMPLES; i++) {
        sum += buffer[i];
    }

    return sum / SMOOTHING_SAMPLES;
}

#endif // CALIBRATION_H
