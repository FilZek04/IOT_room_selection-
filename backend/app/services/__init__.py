"""
Business logic services for the IoT Room Selection system.

Services encapsulate complex business logic separate from API routes:
- ranking_service: Multi-criteria room ranking using AHP
"""

from app.services.ranking_service import ranking_service

__all__ = ["ranking_service"]
