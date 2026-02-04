/**
 * ScoreBreakdown Component
 *
 * Shows detailed breakdown of room scores across different criteria
 *
 * @param {Object} props
 * @param {Object} props.room - Room data with scores
 */
function ScoreBreakdown({ room }) {
  const breakdownItems = [
    {
      label: 'Comfort Score',
      value: room.comfort_score,
      color: 'border-blue-500',
    },
    {
      label: 'Health Score',
      value: room.health_score,
      color: 'border-green-500',
    },
    {
      label: 'Usability Score',
      value: room.usability_score,
      color: 'border-purple-500',
    },
    {
      label: 'Temperature',
      value: room.temperature,
      unit: '°C',
      color: 'border-orange-500',
    },
    {
      label: 'CO2 Level',
      value: room.co2,
      unit: 'ppm',
      color: 'border-cyan-500',
    },
    {
      label: 'Humidity',
      value: room.humidity,
      unit: '%',
      color: 'border-indigo-500',
    },
  ]

  // Add optional metrics if available
  if (room.air_quality !== undefined && room.air_quality !== null) {
    breakdownItems.push({
      label: 'Air Quality',
      value: room.air_quality,
      unit: 'AQI',
      color: 'border-teal-500',
    })
  }

  if (room.voc !== undefined) {
    breakdownItems.push({
      label: 'VOC Level',
      value: room.voc,
      unit: 'ppb',
      color: 'border-pink-500',
    })
  }

  if (room.noise !== undefined) {
    breakdownItems.push({
      label: 'Noise Level',
      value: room.noise,
      unit: 'dBA',
      color: 'border-yellow-500',
    })
  }

  if (room.light !== undefined && room.light !== null) {
    breakdownItems.push({
      label: 'Light Level',
      value: room.light,
      unit: 'lux',
      color: 'border-amber-500',
    })
  }

  if (room.pm25 !== undefined) {
    breakdownItems.push({
      label: 'PM2.5',
      value: room.pm25,
      unit: 'μg/m³',
      color: 'border-rose-500',
    })
  }

  if (room.pm10 !== undefined) {
    breakdownItems.push({
      label: 'PM10',
      value: room.pm10,
      unit: 'μg/m³',
      color: 'border-slate-500',
    })
  }

  return (
    <div className="p-6">
      <h4 className="text-sm font-semibold text-gray-700 mb-4">
        Detailed Score Breakdown
      </h4>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {breakdownItems.map((item) => (
          <div
            key={item.label}
            className={`bg-white rounded-lg p-4 border-l-4 ${item.color}`}
          >
            <div className="text-xs text-gray-600 uppercase tracking-wide mb-1">
              {item.label}
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {item.unit
                ? `${typeof item.value === 'number' ? item.value.toFixed(1) : item.value} ${item.unit}`
                : `${(item.value * 100).toFixed(0)}%`}
            </div>

            {/* Progress bar for scores (values between 0-1) */}
            {!item.unit && (
              <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    item.value >= 0.8
                      ? 'bg-green-500'
                      : item.value >= 0.6
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${item.value * 100}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Room Information */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h5 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
          Room Facilities
        </h5>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
            {room.seating_capacity} Seats
          </span>
          {room.has_projector && (
            <span className="inline-flex items-center px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm font-medium">
              📽️ Projector
            </span>
          )}
          {room.computers > 0 && (
            <span className="inline-flex items-center px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium">
              💻 {room.computers} Computers
            </span>
          )}
          {room.has_robots && (
            <span className="inline-flex items-center px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium">
              🤖 Robots
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default ScoreBreakdown
