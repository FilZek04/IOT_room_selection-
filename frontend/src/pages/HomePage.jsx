import { Link } from 'react-router-dom'
import { Building2, Thermometer, Wind, Users } from 'lucide-react'

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Smart Room Selection System
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Find the perfect room based on environmental conditions and your preferences
        </p>

        <Link
          to="/select-room"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-blue-700 transition"
        >
          Start Room Selection
        </Link>
      </div>

      {/* Features */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <Thermometer className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Temperature</h3>
          <p className="text-gray-600">Optimal comfort based on EU standards</p>
        </div>

        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <Wind className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Air Quality</h3>
          <p className="text-gray-600">CO2 and VOC monitoring</p>
        </div>

        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <Building2 className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Facilities</h3>
          <p className="text-gray-600">Projectors, computers, and equipment</p>
        </div>

        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
            <Users className="w-6 h-6 text-orange-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Personalized</h3>
          <p className="text-gray-600">Customize your preferences</p>
        </div>
      </div>
    </div>
  )
}

export default HomePage
