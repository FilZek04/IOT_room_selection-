import { useState } from 'react'
import { getSaatyInterpretation } from '../utils/ahpCalculations'

/**
 * SaatySlider Component
 *
 * Renders a slider for pairwise comparison using the Saaty 1-9 scale
 *
 * @param {Object} props
 * @param {string} props.criterion1 - First criterion name
 * @param {string} props.criterion2 - Second criterion name
 * @param {number} props.value - Current Saaty scale value (1-9)
 * @param {function} props.onChange - Callback when value changes
 */
function SaatySlider({ criterion1, criterion2, value = 1, onChange }) {
  const [localValue, setLocalValue] = useState(value)

  const handleChange = (e) => {
    const newValue = parseInt(e.target.value)
    setLocalValue(newValue)
    if (onChange) {
      onChange(newValue)
    }
  }

  // Determine which criterion is more important
  const getComparisonText = () => {
    if (localValue === 1) {
      return `Equal importance`
    } else {
      const interpretation = getSaatyInterpretation(localValue)
      return `${criterion1} ${localValue}x more important (${interpretation})`
    }
  }

  return (
    <div className="mb-8">
      {/* Label Row */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          {criterion1} ↔ {criterion2}
        </span>
        <span className="text-sm font-semibold text-blue-600">
          {getComparisonText()}
        </span>
      </div>

        {/* Slider */}
      <div className="relative mb-2">
        <input
          type="range"
          min="1"
          max="9"
          step="1"
          value={localValue}
          onChange={handleChange}
          className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer saaty-slider-${localValue}`}
        />
      </div>

      {/* Scale Labels */}
      <div className="relative text-xs text-gray-500 h-8">
        <span className="absolute left-0 -translate-x-1/2 text-center">Equal<br/>(1)</span>
        <span className="absolute left-1/4 -translate-x-1/2 text-center">Moderate<br/>(3)</span>
        <span className="absolute left-1/2 -translate-x-1/2 text-center">Strong<br/>(5)</span>
        <span className="absolute left-3/4 -translate-x-1/2 text-center">V.Strong<br/>(7)</span>
        <span className="absolute right-0 translate-x-1/2 text-center">Extreme<br/>(9)</span>
      </div>

      <style>{`
        /* Custom slider thumb styling */
        .saaty-slider-${localValue}::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transition: transform 0.15s ease, background-color 0.15s ease;
        }

        .saaty-slider-${localValue}::-webkit-slider-thumb:hover {
          background: #2563eb;
          transform: scale(1.1);
        }

        .saaty-slider-${localValue}::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transition: transform 0.15s ease, background-color 0.15s ease;
        }

        .saaty-slider-${localValue}::-moz-range-thumb:hover {
          background: #2563eb;
          transform: scale(1.1);
        }

        .saaty-slider-${localValue}:focus {
          outline: none;
        }

        .saaty-slider-${localValue}:focus::-webkit-slider-thumb {
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
        }
      `}</style>
    </div>
  )
}

export default SaatySlider
