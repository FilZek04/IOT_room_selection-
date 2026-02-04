"""
API routers for the IoT Room Selection system.

Each router handles a specific domain:
- sensors: Sensor data endpoints (temperature, CO2, etc.)
- facilities: Room and facilities endpoints
- calendar: Calendar and availability endpoints
- ranking: Room ranking/decision support endpoint
"""

from app.routers import sensors, facilities, calendar, ranking

__all__ = ["sensors", "facilities", "calendar", "ranking"]
