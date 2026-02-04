import { useState, useEffect } from 'react'
import { Users, Monitor, Projector, Filter, Bot } from 'lucide-react'

function FacilityRequirements({ onRequirementsChange }) {
  const [requirements, setRequirements] = useState({
    min_seating: '',
    require_projector: false,
    require_computers: false,
    min_robots: '',
  })

  useEffect(() => {
    if (onRequirementsChange) {
      onRequirementsChange({
        min_seating: requirements.min_seating ? parseInt(requirements.min_seating, 10) : null,
        videoprojector: requirements.require_projector || null,
        computers: requirements.require_computers || null,
        min_training_robots: requirements.min_robots ? parseInt(requirements.min_robots, 10) : null,
      })
    }
  }, [requirements, onRequirementsChange])

  const handleSeatingChange = (e) => {
    const value = e.target.value
    if (value === '' || (parseInt(value, 10) >= 0 && parseInt(value, 10) <= 500)) {
      setRequirements((prev) => ({ ...prev, min_seating: value }))
    }
  }

  const handleRobotsChange = (e) => {
    const value = e.target.value
    if (value === '' || (parseInt(value, 10) >= 0 && parseInt(value, 10) <= 200)) {
      setRequirements((prev) => ({ ...prev, min_robots: value }))
    }
  }

  const handleCheckboxChange = (field) => (e) => {
    setRequirements((prev) => ({ ...prev, [field]: e.target.checked }))
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Filter className="w-6 h-6 text-indigo-600" />
        <h2 className="text-xl font-semibold text-gray-800">Room Requirements</h2>
      </div>

      <p className="text-sm text-gray-600 mb-6">
        Specify your hard requirements. Rooms that don&apos;t meet these criteria will be filtered out.
      </p>

      <div className="space-y-6">
        <div>
          <label htmlFor="min-seating" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Users className="w-4 h-4 text-gray-500" />
            Minimum Seats Required
          </label>
          <input
            type="number"
            id="min-seating"
            min="0"
            max="500"
            placeholder="e.g., 25"
            value={requirements.min_seating}
            onChange={handleSeatingChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          />
          <p className="text-xs text-gray-500 mt-1">Leave empty if no minimum required</p>
        </div>

        <div>
          <label htmlFor="min-robots" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Bot className="w-4 h-4 text-gray-500" />
            Minimum Training Robots Required
          </label>
          <input
            type="number"
            id="min-robots"
            min="0"
            max="200"
            placeholder="e.g., 2"
            value={requirements.min_robots}
            onChange={handleRobotsChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          />
          <p className="text-xs text-gray-500 mt-1">Leave empty if no minimum required</p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="require-projector"
            checked={requirements.require_projector}
            onChange={handleCheckboxChange('require_projector')}
            className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
          />
          <label htmlFor="require-projector" className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
            <Projector className="w-4 h-4 text-gray-500" />
            Require Projector
          </label>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="require-computers"
            checked={requirements.require_computers}
            onChange={handleCheckboxChange('require_computers')}
            className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
          />
          <label htmlFor="require-computers" className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
            <Monitor className="w-4 h-4 text-gray-500" />
            Require Computers
          </label>
        </div>

      </div>

      {(requirements.min_seating || requirements.min_robots || requirements.require_projector || requirements.require_computers) && (
        <div className="mt-6 p-4 bg-indigo-50 rounded-lg">
          <h3 className="text-sm font-medium text-indigo-800 mb-2">Active Filters</h3>
          <ul className="text-sm text-indigo-700 space-y-1">
            {requirements.min_seating && (
              <li>• Minimum {requirements.min_seating} seats</li>
            )}
            {requirements.min_robots && (
              <li>• Minimum {requirements.min_robots} training robots</li>
            )}
            {requirements.require_projector && (
              <li>• Must have projector</li>
            )}
            {requirements.require_computers && (
              <li>• Must have computers</li>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}

export default FacilityRequirements
