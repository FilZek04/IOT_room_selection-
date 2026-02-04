import { useState, useEffect } from 'react'

/**
 * RangeSlider Component
 *
 * Single slider for adjusting environmental threshold values
 *
 * @param {Object} props
 * @param {string} props.label - Label for the slider
 * @param {string} props.icon - Icon emoji
 * @param {number} props.value - Current value
 * @param {number} props.min - Minimum value
 * @param {number} props.max - Maximum value
 * @param {number} props.step - Step increment
 * @param {string} props.unit - Unit label (°C, ppm, etc.)
 * @param {number} props.optimalMin - Optimal range minimum
 * @param {number} props.optimalMax - Optimal range maximum
 * @param {function} props.onChange - Callback when value changes
 * @param {string} props.euStandard - EU standard description
 */
function RangeSlider({
  label,
  icon,
  value,
  min,
  max,
  step = 1,
  unit,
  optimalMin,
  optimalMax,
  onChange,
  euStandard,
  hideHeader = false,
}) {
  const [localValue, setLocalValue] = useState(value)

  // Sync local state with prop value (for reset functionality)
  useEffect(() => {
    setLocalValue(value)
  }, [value])

  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value)
    setLocalValue(newValue)
    if (onChange) {
      onChange(newValue)
    }
  }

  // Determine if current value is in optimal range
  const isInOptimalRange = localValue >= optimalMin && localValue <= optimalMax

  // Calculate percentages for visual indicator
  const optimalStartPercent = ((optimalMin - min) / (max - min)) * 100
  const optimalEndPercent = ((optimalMax - min) / (max - min)) * 100

  return (
    <div className={hideHeader ? '' : 'mb-6'}>
      {/* Header */}
      {!hideHeader && (
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{icon}</span>
            <span className="font-medium text-gray-700">{label}</span>
          </div>
          <span className={`text-sm font-semibold ${
            isInOptimalRange ? 'text-green-600' : 'text-orange-600'
          }`}>
            {localValue} {unit}
            {isInOptimalRange && ' ✓'}
          </span>
        </div>
      )}

      {/* Slider with optimal range indicator */}
      <div className="relative mb-2 h-5 flex items-center">
        {/* Optimal range background */}
        <div className="absolute h-2 bg-gray-200 rounded-lg w-full">
          <div
            className="absolute h-full bg-green-100 rounded-lg"
            style={{
              left: `${optimalStartPercent}%`,
              width: `${optimalEndPercent - optimalStartPercent}%`,
            }}
          />
        </div>

        {/* Slider */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={localValue}
          onChange={handleChange}
          className={`absolute w-full bg-transparent appearance-none cursor-pointer z-10 range-slider-${localValue}`}
          style={{ height: '20px' }}
        />
      </div>

      {/* Min/Max Labels */}
      <div className="flex justify-between text-xs text-gray-500 mb-2">
        <span>{min} {unit}</span>
        <span className="text-green-600 font-medium">
          Optimal: {optimalMin}-{optimalMax} {unit}
        </span>
        <span>{max} {unit}</span>
      </div>

      {/* EU Standard Info */}
      {euStandard && (
        <div className="bg-gray-50 rounded px-3 py-2 text-xs text-gray-600">
          <strong>EU Standard:</strong> {euStandard}
        </div>
      )}

      <style>{`
        /* Custom slider thumb styling */
        .range-slider-${localValue}::-webkit-slider-thumb {
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: ${isInOptimalRange ? '#10b981' : '#f59e0b'};
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          position: relative;
          z-index: 20;
          transition: transform 0.15s ease;
        }

        .range-slider-${localValue}::-webkit-slider-thumb:hover {
          transform: scale(1.15);
        }

        .range-slider-${localValue}::-moz-range-thumb {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: ${isInOptimalRange ? '#10b981' : '#f59e0b'};
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transition: transform 0.15s ease;
        }

        .range-slider-${localValue}::-moz-range-thumb:hover {
          transform: scale(1.15);
        }

        .range-slider-${localValue}:focus {
          outline: none;
        }

        .range-slider-${localValue}:focus::-webkit-slider-thumb {
          box-shadow: 0 0 0 3px ${isInOptimalRange ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'};
        }
      `}</style>
    </div>
  )
}

export default RangeSlider
