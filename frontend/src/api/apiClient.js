import axios from 'axios'
import mockApi from './mockApi'

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API !== 'false' // Default to true

// Create axios instance for real API calls
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Convert frontend preferences format to backend format
 * @param {Object} preferences - Frontend preferences
 * @returns {Object} Backend-compatible request format
 */
const transformPreferencesToBackendFormat = (preferences) => {
  const { weights = {}, profile_adjustments = {} } = preferences

  // Helper to convert weight to nearest Saaty scale value (1, 3, 5, 7, 9)
  const toSaatyScale = (weight) => {
    const saatyValues = [1, 3, 5, 7, 9]
    // Convert 0-1 weight to 1-9 scale
    const scaled = 1 + (weight * 8)
    // Find nearest Saaty value
    return saatyValues.reduce((prev, curr) =>
      Math.abs(curr - scaled) < Math.abs(prev - scaled) ? curr : prev
    )
  }

  // Map frontend's 3-tier hierarchy to backend's 6 criteria
  // Comfort → temperature, humidity, sound
  // Health → co2
  // Usability → facilities, availability
  const comfortWeight = weights.Comfort || weights.comfort || 0.40
  const healthWeight = weights.Health || weights.health || 0.35
  const usabilityWeight = weights.Usability || weights.usability || 0.25

  const criteria_weights = {
    temperature: toSaatyScale(comfortWeight * 0.35),
    humidity: toSaatyScale(comfortWeight * 0.25),
    sound: toSaatyScale(comfortWeight * 0.25),
    co2: toSaatyScale(healthWeight),
    facilities: toSaatyScale(usabilityWeight * 0.6),
    availability: toSaatyScale(usabilityWeight * 0.4),
  }

  // Map profile adjustments to environmental preferences
  const environmental_preferences = {}

  if (profile_adjustments.temperature) {
    environmental_preferences.temperature_min = profile_adjustments.temperature.min
    environmental_preferences.temperature_max = profile_adjustments.temperature.max
  }

  if (profile_adjustments.co2) {
    environmental_preferences.co2_max = profile_adjustments.co2.max
  }

  if (profile_adjustments.humidity) {
    environmental_preferences.humidity_min = profile_adjustments.humidity.min
    environmental_preferences.humidity_max = profile_adjustments.humidity.max
  }

  if (profile_adjustments.noise) {
    environmental_preferences.sound_max = profile_adjustments.noise.max
  }

  let facility_requirements = null
    if (preferences.facility_requirements) {
      const fr = preferences.facility_requirements
      facility_requirements = {
        min_seating: fr.min_seating || null,
        videoprojector: fr.videoprojector || null,
        computers: fr.computers || null,
        min_training_robots: fr.min_training_robots || null,
      }
    }

  return {
    criteria_weights,
    environmental_preferences: Object.keys(environmental_preferences).length > 0
      ? environmental_preferences
      : null,
    facility_requirements,
    requested_time: null,
    duration_minutes: null,
  }
}

/**
 * Convert backend response format to frontend format
 * @param {Object} backendData - Backend response
 * @param {Object} originalPreferences - Original frontend preferences for consistency ratio
 * @returns {Object} Frontend-compatible response format
 */
const transformBackendResponseToFrontend = (backendData, originalPreferences = {}) => {
  if (!backendData || !backendData.ranked_rooms) {
    throw new Error('Invalid backend response format')
  }

  const rankings = backendData.ranked_rooms.map(room => {
    const { criteria_scores = {}, current_conditions = {}, facilities = {} } = room

    const pickScore = (candidates, fallback) => {
      for (const key of candidates) {
        const value = criteria_scores[key]
        if (value !== undefined && value !== null) return value
      }
      return fallback
    }

    const averageScores = (candidates) => {
      const values = candidates
        .map((key) => criteria_scores[key])
        .filter((value) => value !== undefined && value !== null)

      if (!values.length) return null
      return values.reduce((sum, value) => sum + value, 0) / values.length
    }

    // Calculate category scores from individual criteria
    const tempScore = pickScore(['temperature', 'Temperature'], 0.8)
    const humidityScore = pickScore(['humidity', 'Humidity'], 0.8)
    const soundScore = pickScore(['sound', 'Noise'], 0.8)
    const lightScore = pickScore(['lighting', 'Lighting'], 0.8)

    const co2Score = pickScore(['co2', 'CO2'], 0.8)
    const vocScore = pickScore(['voc', 'VOC'], 0.8)

    const facilitiesFromSub = averageScores([
      'seating_capacity',
      'SeatingCapacity',
      'equipment',
      'Equipment',
      'av_facilities',
      'AVFacilities',
    ])
    const facilitiesScore = pickScore(['facilities', 'Facilities'], facilitiesFromSub ?? 0.8)
    const availabilityScore = pickScore(['availability', 'Availability'], 1.0)

    // Calculate weighted category scores
    const comfort_score = (tempScore + humidityScore + soundScore + lightScore) / 4
    const health_score = (co2Score + vocScore) / 2
    const usability_score = (facilitiesScore + availabilityScore) / 2

    // Debug: Log light data to help troubleshoot
    const lightValue = current_conditions?.light_intensity ?? current_conditions?.light
    if (import.meta.env.DEV) {
      console.log(`[API Client] Room ${room.room_name} light data:`, {
        light_intensity: current_conditions?.light_intensity,
        light: current_conditions?.light,
        resolved: lightValue
      })
    }

    return {
      rank: room.rank,
      room_id: room.room_name,
      room_name: room.room_name,
      final_score: room.overall_score,
      comfort_score,
      health_score,
      usability_score,
      // Flatten current conditions
      temperature: current_conditions.temperature,
      co2: current_conditions.co2,
      humidity: current_conditions.humidity,
      air_quality: current_conditions.air_quality,
      voc: current_conditions.voc,
      pm25: current_conditions.pm25,
      pm10: current_conditions.pm10,
      noise: current_conditions.sound, // Rename sound → noise
      light: lightValue, // Prefer light_intensity, fallback to light
      // Flatten facilities
      seating_capacity: facilities.seating_capacity,
      has_projector: facilities.videoprojector, // Rename videoprojector → has_projector
      computers: facilities.computers || 0,
      has_robots: facilities.robots_for_training > 0 || false,
    }
  })

  return {
    rankings,
    weights: {
      Comfort: 0.40, // Default weights, could calculate from original preferences
      Health: 0.35,
      Usability: 0.25,
    },
    consistency_ratio: originalPreferences.consistencyRatio || 0.05,
    is_consistent: true,
  }
}

// Request interceptor - add authentication, logging, etc.
axiosInstance.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.data)
    }

    // Add authentication token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => {
    // Log errors
    console.error('[API Response Error]', error)

    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response

      if (status === 401) {
        // Unauthorized - clear auth and redirect to login
        localStorage.removeItem('auth_token')
        // Optionally trigger login redirect
        console.warn('Unauthorized access - authentication required')
      } else if (status === 403) {
        // Forbidden
        console.error('Access forbidden')
      } else if (status === 404) {
        // Not found
        console.error('Resource not found')
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', data)
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server - check if backend is running')
    } else {
      // Other errors
      console.error('Request setup error:', error.message)
    }

    return Promise.reject(error)
  }
)

// API client that switches between mock and real APIs
const apiClient = {
  /**
   * Get all rooms with their sensor data
   * @returns {Promise<Array>} List of rooms
   * @throws {Error} If request fails
   */
  getRooms: async () => {
    if (USE_MOCK) {
      console.log('[API Client] Using mock API for getRooms')
      return mockApi.getRooms()
    }

    try {
      // Backend endpoint: GET /api/v1/rooms/?include_conditions=true
      const response = await axiosInstance.get('/api/v1/rooms/', {
        params: { include_conditions: true }
      })
      return response.data.rooms || response.data
    } catch (error) {
      console.error('[API Client] Error fetching rooms:', error)
      throw new Error(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to fetch rooms'
      )
    }
  },

  /**
   * Evaluate and rank rooms based on user preferences
   * @param {Object} preferences - User preferences and requirements
   * @param {Object} preferences.saaty_preferences - Saaty scale comparisons
   * @param {Object} preferences.weights - Calculated weights
   * @param {Object} preferences.profile_adjustments - Environmental threshold adjustments
   * @returns {Promise<Object>} Rankings and scores
   * @throws {Error} If request fails or validation fails
   */
  evaluateRooms: async (preferences) => {
    if (USE_MOCK) {
      console.log('[API Client] Using mock API for evaluateRooms')
      return mockApi.evaluateRooms(preferences)
    }

    // Validate preferences before sending
    if (!preferences || typeof preferences !== 'object') {
      throw new Error('Preferences must be an object')
    }

    try {
      // Transform frontend preferences to backend format
      const backendRequest = transformPreferencesToBackendFormat(preferences)

      console.log('[API Client] Transformed request:', backendRequest)

      // Backend endpoint: POST /api/v1/rank
      const response = await axiosInstance.post('/api/v1/rank', backendRequest)

      // Transform backend response to frontend format
      const frontendResponse = transformBackendResponseToFrontend(
        response.data,
        preferences
      )

      console.log('[API Client] Transformed response:', frontendResponse)

      // Validate response structure
      if (!frontendResponse || !frontendResponse.rankings) {
        throw new Error('Invalid response format from server')
      }

      return frontendResponse
    } catch (error) {
      console.error('[API Client] Error evaluating rooms:', error)

      // Provide specific error messages
      if (error.response?.status === 400) {
        throw new Error(
          error.response.data?.detail ||
          error.response.data?.message ||
          'Invalid preferences data. Please check your inputs.'
        )
      } else if (error.response?.status === 422) {
        throw new Error(
          'Validation error: ' +
          (error.response.data?.detail || 'Invalid request data')
        )
      }

      throw new Error(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to evaluate rooms'
      )
    }
  },

  /**
   * Health check - test if backend is available
   * @returns {Promise<Object>} Health status
   */
  healthCheck: async () => {
    if (USE_MOCK) {
      return { status: 'ok', mode: 'mock' }
    }

    try {
      const response = await axiosInstance.get('/health')
      return response.data
    } catch {
      throw new Error('Backend is not available')
    }
  },
}

// Export configuration for debugging
export const apiConfig = {
  baseURL: API_BASE_URL,
  useMock: USE_MOCK,
  isDevelopment: import.meta.env.DEV,
}

export default apiClient
