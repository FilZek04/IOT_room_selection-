/**
 * EU Indoor Environmental Quality (IEQ) Standards
 *
 * Based on:
 * - EN 16798-1: Energy performance of buildings - Ventilation for buildings
 * - EN 12464-1: Light and lighting - Lighting of work places
 */

export const SEASONS = {
  WINTER: 'winter',
  SUMMER: 'summer',
}

export const EU_STANDARDS = {
  temperature: {
    min: 18,
    max: 27,
    unit: '°C',
    label: 'Temperature',
    icon: '🌡️',
    description: 'Optimal thermal comfort range based on EN 16798-1 Category II',
    // Winter and summer have different optimal ranges per EN 16798-1
    seasons: {
      [SEASONS.WINTER]: {
        optimalMin: 20,
        optimalMax: 24,
        description: 'Winter heating season (Category II: 20-24°C)',
      },
      [SEASONS.SUMMER]: {
        optimalMin: 23,
        optimalMax: 26,
        description: 'Summer cooling season (Category II: 23-26°C)',
      },
    },
    // Default to winter values for backward compatibility
    optimalMin: 20,
    optimalMax: 24,
    categories: {
      excellent: { min: 20, max: 24 },
      good: { min: 19, max: 25 },
      acceptable: { min: 18, max: 27 },
    },
  },
  co2: {
    min: 400,
    max: 1000,
    optimalMin: 400,
    optimalMax: 800,
    unit: 'ppm',
    label: 'CO2 Level',
    icon: '💨',
    description: 'Indoor air quality (EN 16798-1 Cat II: ≤800ppm optimal, ≤1000ppm acceptable)',
    categories: {
      excellent: { max: 600 },
      good: { max: 800 },
      acceptable: { max: 1000 },
    },
  },
  humidity: {
    min: 30,
    max: 70,
    optimalMin: 40,
    optimalMax: 60,
    unit: '%',
    label: 'Humidity',
    icon: '💧',
    description: 'Relative humidity for comfort and health (EN 16798-1)',
    categories: {
      excellent: { min: 40, max: 60 },
      good: { min: 35, max: 65 },
      acceptable: { min: 30, max: 70 },
    },
  },
  noise: {
    min: 30,
    max: 45,
    optimalMin: 30,
    optimalMax: 35,
    unit: 'dBA',
    label: 'Noise Level',
    icon: '🔇',
    description: 'Noise levels for concentration. Below 35dB is optimal for learning environments',
    categories: {
      excellent: { max: 30 },
      good: { max: 35 },
      acceptable: { max: 45 },
    },
  },
  light: {
    min: 200,
    max: 750,
    optimalMin: 300,
    optimalMax: 500,
    unit: 'lux',
    label: 'Light Level',
    icon: '💡',
    description: 'Illuminance for office work (EN 12464-1)',
    categories: {
      excellent: { min: 300, max: 500 },
      good: { min: 250, max: 600 },
      acceptable: { min: 200, max: 750 },
    },
  },
  voc: {
    min: 0,
    max: 400,
    optimalMin: 0,
    optimalMax: 200,
    unit: 'ppb',
    label: 'VOC Level',
    icon: '🌫️',
    description: 'Volatile Organic Compounds for air quality',
    categories: {
      excellent: { max: 100 },
      good: { max: 200 },
      acceptable: { max: 400 },
    },
  },
  airQuality: {
    min: 0,
    max: 100,
    optimalMin: 0,
    optimalMax: 50,
    unit: 'AQI',
    label: 'Air Quality Index',
    icon: '🍃',
    description: 'Overall air quality indicator',
    categories: {
      excellent: { max: 25 },
      good: { max: 50 },
      acceptable: { max: 100 },
    },
  },
  pm25: {
    min: 0,
    max: 75,
    optimalMin: 0,
    optimalMax: 15,
    unit: 'μg/m³',
    label: 'PM2.5',
    icon: '🌫️',
    description: 'Fine particulate matter (WHO 2021: 15μg/m³ 24h mean)',
    categories: {
      excellent: { max: 5 },
      good: { max: 15 },
      acceptable: { max: 35 },
    },
  },
  pm10: {
    min: 0,
    max: 150,
    optimalMin: 0,
    optimalMax: 45,
    unit: 'μg/m³',
    label: 'PM10',
    icon: '💨',
    description: 'Coarse particulate matter (WHO 2021: 45μg/m³ 24h mean)',
    categories: {
      excellent: { max: 15 },
      good: { max: 45 },
      acceptable: { max: 75 },
    },
  },
}

/**
 * Get default profile based on EU standards (optimal values)
 * @param {string} season - 'winter' or 'summer' (default: 'winter')
 */
export function getDefaultProfile(season = SEASONS.WINTER) {
  const profile = {}

  Object.keys(EU_STANDARDS).forEach((key) => {
    const standard = EU_STANDARDS[key]
    
    // Handle temperature season-specific values
    if (key === 'temperature' && standard.seasons) {
      const seasonData = standard.seasons[season] || standard.seasons[SEASONS.WINTER]
      profile[key] = {
        min: seasonData.optimalMin,
        max: seasonData.optimalMax,
      }
    } else {
      profile[key] = {
        min: standard.optimalMin,
        max: standard.optimalMax,
      }
    }
  })

  return profile
}

/**
 * Check if a value is within optimal range
 */
export function isOptimal(criterion, value) {
  const standard = EU_STANDARDS[criterion]
  if (!standard) return false

  if (standard.optimalMin !== undefined && value < standard.optimalMin) return false
  if (standard.optimalMax !== undefined && value > standard.optimalMax) return false

  return true
}

/**
 * Get category for a value (excellent, good, acceptable, poor)
 */
export function getCategory(criterion, value) {
  const standard = EU_STANDARDS[criterion]
  if (!standard) return 'unknown'

  const { categories } = standard

  // Check excellent
  if (categories.excellent) {
    const { min, max } = categories.excellent
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'excellent'
    }
  }

  // Check good
  if (categories.good) {
    const { min, max } = categories.good
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'good'
    }
  }

  // Check acceptable
  if (categories.acceptable) {
    const { min, max } = categories.acceptable
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'acceptable'
    }
  }

  return 'poor'
}
