// Mock API using real sensor data from docs/project info&data/Project_sensor_data/aggregated_rooms.json
// This simulates what the FastAPI backend will do

// Import room data from project data
// Note: In production, this will be fetched from the backend
import roomsData from '../../../docs/project info&data/Project_sensor_data/aggregated_rooms.json'
import { EU_STANDARDS } from '../constants/euStandards'

/**
 * Score a single criterion based on user's threshold
 * Returns 1.0 if within optimal range, scales down as it gets further away
 */
const scoreCriterion = (value, userMin, userMax, absoluteMin, absoluteMax) => {
  // If no value, return 0
  if (value === undefined || value === null) return 0

  // If within user's optimal range, perfect score
  if (value >= userMin && value <= userMax) return 1.0

  // Calculate how far outside the optimal range
  // The further away, the lower the score
  if (value < userMin) {
    const range = userMin - absoluteMin
    const distance = userMin - value
    return Math.max(0, 1 - (distance / range) * 0.7) // Max penalty 0.7
  } else {
    const range = absoluteMax - userMax
    const distance = value - userMax
    return Math.max(0, 1 - (distance / range) * 0.7) // Max penalty 0.7
  }
}

/**
 * Calculate comfort score based on environmental factors
 */
const calculateComfortScore = (room, profile) => {
  const tempProfile = profile.temperature || { min: 20, max: 24 }
  const humidProfile = profile.humidity || { min: 40, max: 60 }
  const noiseProfile = profile.noise || { min: 30, max: 35 }
  const lightProfile = profile.light || { min: 300, max: 500 }

  const tempScore = scoreCriterion(
    room.temperature,
    tempProfile.min,
    tempProfile.max,
    EU_STANDARDS.temperature.min,
    EU_STANDARDS.temperature.max
  )

  const humidScore = scoreCriterion(
    room.humidity,
    humidProfile.min,
    humidProfile.max,
    EU_STANDARDS.humidity.min,
    EU_STANDARDS.humidity.max
  )

  const noiseScore = room.noise
    ? scoreCriterion(
        room.noise,
        noiseProfile.min,
        noiseProfile.max,
        EU_STANDARDS.noise.min,
        EU_STANDARDS.noise.max
      )
    : 0.8 // Default if no noise data

  const lightScore = room.light
    ? scoreCriterion(
        room.light,
        lightProfile.min,
        lightProfile.max,
        EU_STANDARDS.light.min,
        EU_STANDARDS.light.max
      )
    : 0.8 // Default if no light data

  // Weight the comfort factors
  return tempScore * 0.35 + humidScore * 0.25 + noiseScore * 0.2 + lightScore * 0.2
}

/**
 * Calculate health score based on air quality factors
 */
const calculateHealthScore = (room, profile) => {
  const co2Profile = profile.co2 || { min: 400, max: 800 }
  const vocProfile = profile.voc || { min: 0, max: 200 }
  const pm25Profile = profile.pm25 || { min: 0, max: 15 }
  const pm10Profile = profile.pm10 || { min: 0, max: 45 }

  const co2Score = scoreCriterion(
    room.co2,
    co2Profile.min,
    co2Profile.max,
    EU_STANDARDS.co2.min,
    EU_STANDARDS.co2.max
  )

  const aqScore = room.air_quality
    ? scoreCriterion(
        room.air_quality,
        0,
        50,
        EU_STANDARDS.airQuality.min,
        EU_STANDARDS.airQuality.max
      )
    : 0.8

  const vocScore = room.voc
    ? scoreCriterion(
        room.voc,
        vocProfile.min,
        vocProfile.max,
        EU_STANDARDS.voc.min,
        EU_STANDARDS.voc.max
      )
    : 0.8

  const pm25Score = room.pm25
    ? scoreCriterion(
        room.pm25,
        pm25Profile.min,
        pm25Profile.max,
        EU_STANDARDS.pm25.min,
        EU_STANDARDS.pm25.max
      )
    : 0.8

  const pm10Score = room.pm10
    ? scoreCriterion(
        room.pm10,
        pm10Profile.min,
        pm10Profile.max,
        EU_STANDARDS.pm10.min,
        EU_STANDARDS.pm10.max
      )
    : 0.8

  // Weight the health factors: CO2 40%, AQ 20%, VOC 15%, PM2.5 15%, PM10 10%
  return co2Score * 0.4 + aqScore * 0.2 + vocScore * 0.15 + pm25Score * 0.15 + pm10Score * 0.1
}

/**
 * Calculate usability score based on facilities
 */
const calculateUsabilityScore = (room) => {
  let score = 0.5 // Base score

  // Projector adds value
  if (room.has_projector) score += 0.2

  // Computers add value
  if (room.computers > 0) {
    score += Math.min(0.3, room.computers / 100) // More computers = better, up to 0.3
  }

  // Robots add value
  if (room.has_robots) score += 0.15

  // Seating capacity
  if (room.seating_capacity >= 30) {
    score += 0.1 // Large room bonus
  }

  return Math.min(1.0, score) // Cap at 1.0
}

export const mockApi = {
  // GET /api/rooms - List all rooms with their data
  getRooms: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(roomsData)
      }, 300) // Simulate network delay
    })
  },

  // POST /api/evaluate - Evaluate and rank rooms based on preferences
  evaluateRooms: async (preferences = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Extract user preferences
        const profile = preferences.profile_adjustments || {}
        const weights = preferences.weights || {
          Comfort: 0.40,
          Health: 0.35,
          Usability: 0.25,
        }

        console.log('[Mock API] Evaluating with preferences:', {
          weights,
          profile,
        })

        // Score each room using user's preferences
        const scoredRooms = roomsData.map((room) => {
          const comfortScore = calculateComfortScore(room, profile)
          const healthScore = calculateHealthScore(room, profile)
          const usabilityScore = calculateUsabilityScore(room)

          // Calculate weighted final score using user's weights
          const finalScore =
            comfortScore * weights.Comfort +
            healthScore * weights.Health +
            usabilityScore * weights.Usability

          return {
            ...room,
            comfort_score: comfortScore,
            health_score: healthScore,
            usability_score: usabilityScore,
            final_score: finalScore,
          }
        })

        // Sort by final score (descending)
        const ranked = scoredRooms
          .sort((a, b) => b.final_score - a.final_score)
          .map((room, index) => ({
            rank: index + 1,
            room_id: room.room_id,
            room_name: room.name,
            final_score: room.final_score,
            comfort_score: room.comfort_score,
            health_score: room.health_score,
            usability_score: room.usability_score,
            temperature: room.temperature,
            co2: room.co2,
            humidity: room.humidity,
            air_quality: room.air_quality,
            voc: room.voc,
            pm25: room.pm25,
            pm10: room.pm10,
            noise: room.noise,
            light: room.light,
            seating_capacity: room.seating_capacity,
            has_projector: room.has_projector,
            computers: room.computers,
            has_robots: room.has_robots,
          }))

        console.log('[Mock API] Top 3 ranked rooms:', ranked.slice(0, 3))

        resolve({
          rankings: ranked,
          weights: weights,
          consistency_ratio: preferences.consistencyRatio || 0.05,
          is_consistent: true,
        })
      }, 500) // Simulate network delay
    })
  },

  // GET /api/criteria - Get AHP criteria hierarchy
  getCriteria: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          main: ['Comfort', 'Health', 'Usability'],
          comfort: ['Temperature', 'Lighting', 'Noise', 'Humidity'],
          health: ['CO2', 'Air Quality', 'VOC', 'PM2.5', 'PM10'],
          usability: ['Seating', 'Equipment', 'AV Facilities'],
          weights: {
            main: {
              Comfort: 0.40,
              Health: 0.35,
              Usability: 0.25,
            },
            comfort: {
              Temperature: 0.35,
              Lighting: 0.25,
              Noise: 0.25,
              Humidity: 0.15,
            },
            health: {
              CO2: 0.40,
              'Air Quality': 0.20,
              VOC: 0.15,
              'PM2.5': 0.15,
              PM10: 0.10,
            },
            usability: {
              Seating: 0.50,
              Equipment: 0.30,
              'AV Facilities': 0.20,
            },
          },
        })
      }, 200)
    })
  },
}

export default mockApi
