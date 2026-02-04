import { useState, useMemo, useEffect } from 'react'
import SaatySlider from './SaatySlider'
import { calculateAHPWeights } from '../utils/ahpCalculations'
import { AlertCircle, CheckCircle2 } from 'lucide-react'

/**
 * PreferenceMatrix Component
 *
 * Manages pairwise comparisons for main criteria using Saaty scale
 * Calculates and displays weights and consistency ratio in real-time
 */
function PreferenceMatrix({ onPreferencesChange }) {
  // Main criteria for room selection (memoized to prevent dependency changes)
  const criteria = useMemo(() => ['Comfort', 'Health', 'Usability'], [])

  // State for pairwise comparisons
  const [comparisons, setComparisons] = useState({
    'Comfort-Health': 3,      // Comfort moderately more important than Health
    'Comfort-Usability': 5,   // Comfort strongly more important than Usability
    'Health-Usability': 2,    // Health weakly more important than Usability
  })

  // Calculated weights and consistency ratio (derived state, no setState in effect)
  const results = useMemo(() => calculateAHPWeights(criteria, comparisons), [criteria, comparisons])

  // Notify parent component whenever results change
  useEffect(() => {
    if (onPreferencesChange) {
      onPreferencesChange({
        comparisons,
        weights: results.weights,
        consistencyRatio: results.consistencyRatio,
      })
    }
  }, [comparisons, results, onPreferencesChange])

  // Handle slider value change
  const handleComparisonChange = (key, value) => {
    setComparisons((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  // Format percentage for display
  const formatPercent = (value) => {
    return `${Math.round(value * 100)}%`
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Criteria Importance (Saaty Scale)
        </h2>
        <p className="text-sm text-gray-600">
          Compare criteria pairwise using the Saaty 1-9 scale to express your preferences
        </p>
      </div>

      {/* Saaty Sliders */}
      <div className="space-y-6">
        <SaatySlider
          criterion1="Comfort"
          criterion2="Health"
          value={comparisons['Comfort-Health']}
          onChange={(value) => handleComparisonChange('Comfort-Health', value)}
        />

        <SaatySlider
          criterion1="Comfort"
          criterion2="Usability"
          value={comparisons['Comfort-Usability']}
          onChange={(value) => handleComparisonChange('Comfort-Usability', value)}
        />

        <SaatySlider
          criterion1="Health"
          criterion2="Usability"
          value={comparisons['Health-Usability']}
          onChange={(value) => handleComparisonChange('Health-Usability', value)}
        />
      </div>

      {/* Calculated Weights Display */}
      <div className="mt-8 bg-gray-50 rounded-lg p-5">
        <h3 className="font-semibold text-gray-900 mb-4">Calculated Weights:</h3>
        <div className="space-y-3">
          {criteria.map((criterion) => (
            <div key={criterion} className="flex justify-between items-center">
              <span className="text-gray-700">{criterion}</span>
              <div className="flex items-center gap-3">
                <div className="w-32 bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: formatPercent(results.weights[criterion]) }}
                  ></div>
                </div>
                <span className="text-blue-600 font-semibold min-w-[50px] text-right">
                  {formatPercent(results.weights[criterion])}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Consistency Ratio */}
      <div className={`mt-5 p-4 rounded-lg border-l-4 ${
        results.isConsistent
          ? 'bg-green-50 border-green-500'
          : 'bg-yellow-50 border-yellow-500'
      }`}>
        <div className="flex items-center gap-2">
          {results.isConsistent ? (
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          )}
          <div className="flex-1">
            <p className={`text-sm font-medium ${
              results.isConsistent ? 'text-green-900' : 'text-yellow-900'
            }`}>
              Consistency Ratio: {results.consistencyRatio.toFixed(3)}
            </p>
            <p className={`text-xs mt-1 ${
              results.isConsistent ? 'text-green-700' : 'text-yellow-700'
            }`}>
              {results.isConsistent
                ? '✓ Acceptable (CR < 0.1) - Your comparisons are logically consistent'
                : '⚠ Warning (CR ≥ 0.1) - Consider revising your comparisons for better consistency'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Saaty Scale Reference */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          Saaty Scale Reference:
        </h4>
        <div className="text-xs text-blue-800 space-y-1">
          <div><strong>1:</strong> Equal importance</div>
          <div><strong>3:</strong> Moderate importance</div>
          <div><strong>5:</strong> Strong importance</div>
          <div><strong>7:</strong> Very strong importance</div>
          <div><strong>9:</strong> Extreme importance</div>
          <div className="text-blue-600 italic mt-2">
            Even values (2, 4, 6, 8) represent intermediate judgments
          </div>
        </div>
      </div>
    </div>
  )
}

export default PreferenceMatrix
