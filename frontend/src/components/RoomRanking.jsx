import { useState, Fragment } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { EU_STANDARDS } from '../constants/euStandards'
import ScoreBreakdown from './ScoreBreakdown'

/**
 * RoomRanking Component
 *
 * Displays ranked rooms with scores and expandable breakdowns
 *
 * @param {Object} props
 * @param {Array} props.rankings - Array of ranked rooms
 * @param {number} props.consistencyRatio - AHP consistency ratio
 */
function RoomRanking({ rankings = [], consistencyRatio = 0 }) {
  const [expandedRows, setExpandedRows] = useState(new Set())

  const toggleRow = (roomId) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(roomId)) {
      newExpanded.delete(roomId)
    } else {
      newExpanded.add(roomId)
    }
    setExpandedRows(newExpanded)
  }

  const getRankBadgeClass = (rank) => {
    if (rank === 1) return 'bg-gradient-to-br from-yellow-400 to-orange-400'
    if (rank === 2) return 'bg-gradient-to-br from-gray-300 to-gray-600'
    if (rank === 3) return 'bg-gradient-to-br from-pink-400 to-orange-300'
    return 'bg-indigo-600'
  }

  const getStatusBadge = (value, ranges) => {
    const {
      optimalMin,
      optimalMax,
      acceptableMin,
      acceptableMax,
    } = ranges
    const isOptimal = value >= optimalMin && value <= optimalMax
    const isAcceptable = value >= acceptableMin && value <= acceptableMax

    if (isOptimal) {
      return {
        icon: '✓',
        className: 'bg-green-100 text-green-800',
      }
    } else if (isAcceptable) {
      return {
        icon: '⚠',
        className: 'bg-yellow-100 text-yellow-800',
      }
    } else {
      return {
        icon: '✗',
        className: 'bg-red-100 text-red-800',
      }
    }
  }

  if (!rankings || rankings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500">
          No rooms to display. Please adjust your preferences and evaluate rooms.
        </p>
      </div>
    )
  }

  const topScore = rankings[0]?.final_score || 0
  const bestRoom = rankings[0]?.room_name || 'N/A'

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">{rankings.length}</div>
          <div className="text-sm text-gray-600 mt-1">Rooms Evaluated</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">
            {consistencyRatio.toFixed(3)}
          </div>
          <div className="text-sm text-gray-600 mt-1">Consistency Ratio</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">{bestRoom}</div>
          <div className="text-sm text-gray-600 mt-1">Best Match</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">
            {(topScore * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600 mt-1">Top Score</div>
        </div>
      </div>

      {/* Rankings Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-indigo-600 text-white">
              <tr>
                <th className="px-4 py-3 text-center text-sm font-semibold">Rank</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Room Name</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Overall Score</th>
                <th className="px-4 py-3 text-center text-sm font-semibold">Temp</th>
                <th className="px-4 py-3 text-center text-sm font-semibold">CO2</th>
                <th className="px-4 py-3 text-center text-sm font-semibold">Humidity</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Facilities</th>
                <th className="px-4 py-3 text-center text-sm font-semibold">Details</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((room) => {
                const isExpanded = expandedRows.has(room.room_id)
                const tempStandard = EU_STANDARDS.temperature
                const co2Standard = EU_STANDARDS.co2
                const humidityStandard = EU_STANDARDS.humidity
                const tempStatus = getStatusBadge(room.temperature, {
                  optimalMin: tempStandard.optimalMin,
                  optimalMax: tempStandard.optimalMax,
                  acceptableMin: tempStandard.categories.acceptable.min,
                  acceptableMax: tempStandard.categories.acceptable.max,
                })
                const co2Status = getStatusBadge(room.co2, {
                  optimalMin: co2Standard.optimalMin,
                  optimalMax: co2Standard.optimalMax,
                  acceptableMin: co2Standard.min,
                  acceptableMax: co2Standard.categories.acceptable.max,
                })
                const humidityStatus = getStatusBadge(room.humidity, {
                  optimalMin: humidityStandard.optimalMin,
                  optimalMax: humidityStandard.optimalMax,
                  acceptableMin: humidityStandard.categories.acceptable.min,
                  acceptableMax: humidityStandard.categories.acceptable.max,
                })

                return (
                  <Fragment key={room.room_id}>
                    {/* Main Row */}
                    <tr className="border-b border-gray-200 hover:bg-gray-50 transition">
                      {/* Rank Badge */}
                      <td className="px-4 py-4 text-center">
                        <span
                          className={`w-8 h-8 rounded-full inline-flex items-center justify-center text-white font-bold text-sm ${getRankBadgeClass(
                            room.rank
                          )}`}
                        >
                          {room.rank}
                        </span>
                      </td>

                      {/* Room Name */}
                      <td className="px-4 py-4">
                        <span className="font-semibold text-gray-900">{room.room_name}</span>
                      </td>

                      {/* Overall Score */}
                      <td className="px-4 py-4">
                        <div className="text-sm font-semibold text-green-600 mb-1">
                          {(room.final_score * 100).toFixed(0)}%
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all"
                            style={{ width: `${room.final_score * 100}%` }}
                          />
                        </div>
                      </td>

                      {/* Temperature */}
                      <td className="px-4 py-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${tempStatus.className}`}
                        >
                          {tempStatus.icon} {room.temperature.toFixed(1)}°C
                        </span>
                      </td>

                      {/* CO2 */}
                      <td className="px-4 py-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${co2Status.className}`}
                        >
                          {co2Status.icon} {Math.round(room.co2)}
                        </span>
                      </td>

                      {/* Humidity */}
                      <td className="px-4 py-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${humidityStatus.className}`}
                        >
                          {humidityStatus.icon} {room.humidity.toFixed(1)}%
                        </span>
                      </td>

                      {/* Facilities */}
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          {room.has_projector && (
                            <span title="Projector" className="text-lg">
                              📽️
                            </span>
                          )}
                          {room.computers > 0 && (
                            <span title={`${room.computers} Computers`} className="text-lg">
                              💻
                            </span>
                          )}
                          {room.has_robots && (
                            <span title="Robots" className="text-lg">
                              🤖
                            </span>
                          )}
                          <span className="text-xs text-gray-600">
                            {room.seating_capacity} seats
                          </span>
                        </div>
                      </td>

                      {/* Details Button */}
                      <td className="px-4 py-4 text-center">
                        <button
                          onClick={() => toggleRow(room.room_id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition"
                        >
                          {isExpanded ? (
                            <>
                              Hide <ChevronUp className="w-4 h-4" />
                            </>
                          ) : (
                            <>
                              Show <ChevronDown className="w-4 h-4" />
                            </>
                          )}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Breakdown */}
                    {isExpanded && (
                      <tr className="bg-gray-50">
                        <td colSpan={8} className="p-0">
                          <ScoreBreakdown room={room} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default RoomRanking
