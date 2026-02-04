import { useState, useEffect } from 'react'
import RangeSlider from './RangeSlider'
import { EU_STANDARDS, getDefaultProfile, SEASONS } from '../constants/euStandards'
import { RotateCcw, Sun, Snowflake } from 'lucide-react'

function ProfileAdjuster({ onProfileChange }) {
  const [season, setSeason] = useState(SEASONS.WINTER)
  const [profile, setProfile] = useState(getDefaultProfile(season))
  const displayCriteria = ['temperature', 'co2', 'humidity', 'noise', 'light', 'voc', 'pm25', 'pm10']

  useEffect(() => {
    const newProfile = getDefaultProfile(season)
    setProfile(newProfile)
  }, [season])

  useEffect(() => {
    if (onProfileChange) {
      onProfileChange(profile)
    }
  }, [profile, onProfileChange])

  const handleSeasonChange = (newSeason) => {
    setSeason(newSeason)
  }

  const handleCriterionChange = (criterion, value) => {
    setProfile((prev) => ({
      ...prev,
      [criterion]: {
        min: prev[criterion]?.min || EU_STANDARDS[criterion].optimalMin,
        max: value,
      },
    }))
  }

  const handleReset = () => {
    setProfile(getDefaultProfile(season))
  }

  const getCurrentValue = (criterion) => {
    return profile[criterion]?.max || EU_STANDARDS[criterion].optimalMax
  }

  const getOptimalRange = (criterion) => {
    if (criterion === 'temperature' && EU_STANDARDS[criterion].seasons) {
      return EU_STANDARDS[criterion].seasons[season]
    }
    return {
      optimalMin: EU_STANDARDS[criterion].optimalMin,
      optimalMax: EU_STANDARDS[criterion].optimalMax,
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Environmental Thresholds
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Adjust your ideal ranges for environmental conditions
            </p>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition"
            title="Reset to EU Standards"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
        </div>

      </div>

      <div className="space-y-6">
        {displayCriteria.map((criterion) => {
          const standard = EU_STANDARDS[criterion]
          const optimalRange = getOptimalRange(criterion)
          
          // Render temperature with inline season toggle
          if (criterion === 'temperature') {
            const tempValue = getCurrentValue(criterion)
            const isOptimal = tempValue >= optimalRange.optimalMin && tempValue <= optimalRange.optimalMax
            return (
              <div key={criterion} className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{standard.icon}</span>
                    <span className="font-medium text-gray-700">{standard.label}</span>
                    <div className="flex items-center gap-1 ml-2">
                      <button
                        onClick={() => handleSeasonChange(SEASONS.WINTER)}
                        className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition ${
                          season === SEASONS.WINTER
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                        title="Winter: 20-24°C"
                      >
                        <Snowflake className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => handleSeasonChange(SEASONS.SUMMER)}
                        className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition ${
                          season === SEASONS.SUMMER
                            ? 'bg-orange-500 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                        title="Summer: 23-26°C"
                      >
                        <Sun className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                  <span className={`text-sm font-semibold ${isOptimal ? 'text-green-600' : 'text-orange-600'}`}>
                    {tempValue} {standard.unit}
                    {isOptimal && ' ✓'}
                  </span>
                </div>
                <RangeSlider
                  label=""
                  icon=""
                  value={getCurrentValue(criterion)}
                  min={standard.min}
                  max={standard.max}
                  step={0.5}
                  unit={standard.unit}
                  optimalMin={optimalRange.optimalMin}
                  optimalMax={optimalRange.optimalMax}
                  onChange={(value) => handleCriterionChange(criterion, value)}
                  euStandard={standard.description}
                  hideHeader
                />
              </div>
            )
          }
          
          return (
            <RangeSlider
              key={criterion}
              label={standard.label}
              icon={standard.icon}
              value={getCurrentValue(criterion)}
              min={standard.min}
              max={standard.max}
              step={
                criterion === 'humidity'
                  ? 0.5
                  : criterion === 'noise'
                    ? 1
                    : criterion === 'pm25' || criterion === 'pm10'
                      ? 1
                      : 10
              }
              unit={standard.unit}
              optimalMin={optimalRange.optimalMin}
              optimalMax={optimalRange.optimalMax}
              onChange={(value) => handleCriterionChange(criterion, value)}
              euStandard={standard.description}
            />
          )
        })}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          About Environmental Thresholds
        </h4>
        <p className="text-xs text-blue-800 leading-relaxed">
          These thresholds define your acceptable ranges for each environmental factor.
          Values follow EN 16798-1 (thermal comfort and air quality), EN 12464-1 (lighting),
          and WHO particulate guidance; remaining ranges are project-defined defaults.
          Rooms with readings within your specified ranges will score higher in the evaluation.
        </p>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">
          Current Profile Summary
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {displayCriteria.map((criterion) => {
            const standard = EU_STANDARDS[criterion]
            const current = getCurrentValue(criterion)
            const optimalRange = getOptimalRange(criterion)
            const isOptimal = current === optimalRange.optimalMax
            return (
              <div key={criterion} className="flex justify-between items-center">
                <span className="text-gray-600">
                  {standard.icon} {standard.label}:
                </span>
                <span className={`font-medium ${
                  isOptimal ? 'text-green-600' : 'text-blue-600'
                }`}>
                  ≤ {current} {standard.unit}
                  {isOptimal && ' ✓'}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ProfileAdjuster
