import SwaggerUI from 'swagger-ui-react'
import 'swagger-ui-react/swagger-ui.css'
import { apiConfig } from '../api/apiClient'
import { AlertCircle, ExternalLink } from 'lucide-react'

/**
 * SwaggerDocs Component
 *
 * Embeds Swagger UI to display FastAPI documentation
 * Falls back to mock mode notice when backend is not available
 */
function SwaggerDocs() {
  // Swagger JSON URL from backend
  const swaggerUrl = `${apiConfig.baseURL}/openapi.json`

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">API Documentation</h1>
              <p className="mt-2 text-sm text-gray-600">
                Interactive documentation for the IoT Room Selection API
              </p>
            </div>
            <a
              href="/"
              className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition"
            >
              ← Back to App
            </a>
          </div>
        </div>
      </div>

      {/* Mock Mode Notice */}
      {apiConfig.useMock && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-yellow-800 mb-1">
                Mock API Mode Active
              </h3>
              <p className="text-sm text-yellow-700 mb-2">
                The frontend is currently using a mock API. To view the real API documentation, start the FastAPI backend and set <code className="bg-yellow-100 px-1 rounded">VITE_USE_MOCK_API=false</code> in your environment.
              </p>
              <div className="text-sm text-yellow-700">
                <strong>To start the backend:</strong>
                <pre className="mt-1 bg-yellow-100 p-2 rounded text-xs overflow-x-auto">
                  cd backend{'\n'}
                  uvicorn app.main:app --reload
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Backend Available Notice */}
      {!apiConfig.useMock && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <div className="flex-1">
              <p className="text-sm text-blue-700">
                Viewing live API documentation from:{' '}
                <a
                  href={`${apiConfig.baseURL}/docs`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold hover:underline inline-flex items-center gap-1"
                >
                  {apiConfig.baseURL}/docs
                  <ExternalLink className="w-3 h-3" />
                </a>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Swagger UI */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {!apiConfig.useMock ? (
            <SwaggerUI
              url={swaggerUrl}
              docExpansion="list"
              defaultModelsExpandDepth={1}
              displayRequestDuration={true}
              filter={true}
              tryItOutEnabled={true}
            />
          ) : (
            // Mock API - Show placeholder
            <div className="p-12 text-center">
              <div className="max-w-md mx-auto">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  API Documentation Not Available
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  The mock API doesn't provide Swagger documentation. Start the FastAPI backend to view interactive API docs.
                </p>
                <div className="bg-gray-50 rounded-lg p-4 text-left">
                  <p className="text-xs font-semibold text-gray-700 mb-2">Mock API Endpoints:</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    <li>• <code className="bg-gray-200 px-1 rounded">GET /api/rooms</code> - List all rooms</li>
                    <li>• <code className="bg-gray-200 px-1 rounded">POST /api/evaluate</code> - Evaluate and rank rooms</li>
                    <li>• <code className="bg-gray-200 px-1 rounded">GET /api/criteria</code> - Get AHP criteria hierarchy</li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3">
                    See <code className="bg-gray-200 px-1 rounded">frontend/src/api/mockApi.js</code> for implementation details.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Additional Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">About the API</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Technology Stack</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• <strong>Backend:</strong> FastAPI (Python)</li>
                <li>• <strong>Algorithm:</strong> AHP (Analytic Hierarchy Process)</li>
                <li>• <strong>Database:</strong> MongoDB</li>
                <li>• <strong>Documentation:</strong> OpenAPI 3.0</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Related Resources</h3>
              <ul className="text-gray-600 space-y-1">
                <li>
                  • <a href={`${apiConfig.baseURL}/docs`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                    Swagger UI (External)
                  </a>
                </li>
                <li>
                  • <a href={`${apiConfig.baseURL}/redoc`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                    ReDoc (External)
                  </a>
                </li>
                <li>
                  • <a href="/docs/frontend/API-Integration-Guide.md" className="text-indigo-600 hover:underline">
                    API Integration Guide
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SwaggerDocs
