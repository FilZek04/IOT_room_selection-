import { useState, useCallback } from 'react'
import apiClient from '../api/apiClient'

/**
 * Custom hook for managing room ranking state and API calls
 *
 * @returns {Object} Hook state and functions
 * @returns {Array|null} rankings - Current room rankings
 * @returns {boolean} loading - Loading state
 * @returns {string|null} error - Error message if any
 * @returns {Function} evaluateRooms - Function to evaluate rooms
 * @returns {Function} clearRankings - Function to clear rankings
 * @returns {Function} clearError - Function to clear error
 *
 * @example
 * const { rankings, loading, error, evaluateRooms } = useRoomRanking()
 *
 * const handleSubmit = async () => {
 *   await evaluateRooms({
 *     saaty_preferences: comparisons,
 *     weights: weights,
 *     profile_adjustments: profile
 *   })
 * }
 */
function useRoomRanking() {
  const [rankings, setRankings] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  /**
   * Evaluate rooms based on user preferences
   * @param {Object} preferences - User preferences
   * @param {Object} preferences.saaty_preferences - Pairwise comparisons
   * @param {Object} preferences.weights - Calculated weights
   * @param {Object} preferences.profile_adjustments - Environmental thresholds
   * @returns {Promise<Object>} Rankings result
   */
  const evaluateRooms = useCallback(async (preferences) => {
    setLoading(true)
    setError(null)

    try {
      // Validate preferences before sending
      if (!preferences) {
        throw new Error('Preferences are required')
      }

      // Call API
      const result = await apiClient.evaluateRooms(preferences)

      // Validate response
      if (!result || !result.rankings) {
        throw new Error('Invalid response from server')
      }

      // Check if rankings array is empty
      if (result.rankings.length === 0) {
        throw new Error('No rooms match your criteria')
      }

      setRankings(result)
      return result
    } catch (err) {
      // Handle different error types
      let errorMessage = 'Failed to evaluate rooms'

      if (err.response) {
        // Server responded with error status
        const status = err.response.status
        if (status === 400) {
          errorMessage = 'Invalid preferences. Please check your inputs.'
        } else if (status === 404) {
          errorMessage = 'API endpoint not found. Backend may not be running.'
        } else if (status === 500) {
          errorMessage = 'Server error. Please try again later.'
        } else if (status === 503) {
          errorMessage = 'Service unavailable. Backend may be down.'
        } else {
          errorMessage = err.response.data?.message || errorMessage
        }
      } else if (err.request) {
        // Request made but no response received
        errorMessage = 'Cannot connect to backend. Please check if the server is running.'
      } else if (err.message) {
        // Other errors (validation, etc.)
        errorMessage = err.message
      }

      console.error('Error evaluating rooms:', err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Clear current rankings
   */
  const clearRankings = useCallback(() => {
    setRankings(null)
    setError(null)
  }, [])

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    rankings,
    loading,
    error,
    evaluateRooms,
    clearRankings,
    clearError,
  }
}

export default useRoomRanking
