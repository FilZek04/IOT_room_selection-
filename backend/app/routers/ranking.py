from fastapi import APIRouter, HTTPException
import logging

from app.models.ranking import RankingRequest, RankingResponse
from app.services.ranking_service import ranking_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=RankingResponse,
    summary="Rank rooms based on preferences",
    description="Ranks available rooms using AHP multi-criteria decision making."
)
async def rank_rooms(request: RankingRequest):
    """Rank rooms based on user preferences using AHP."""
    try:
        logger.info(f"Ranking request received with criteria weights: {request.criteria_weights}")

        response = await ranking_service.rank_rooms(request)

        logger.info(f"Ranking completed: {response.total_rooms_evaluated} rooms evaluated")

        return response

    except Exception as e:
        logger.error(f"Error during room ranking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ranking rooms: {str(e)}"
        )


@router.get(
    "/example",
    summary="Get an example ranking request",
    description="Returns an example ranking request body that you can use as a template."
)
async def get_example_request():
    """Get an example ranking request for documentation."""
    return {
        "example_1_focused_work": {
            "description": "Looking for a quiet room with good air quality for focused work",
            "request": {
                "criteria_weights": {
                    "temperature": 5,
                    "co2": 7,
                    "humidity": 3,
                    "sound": 9,
                    "facilities": 3,
                    "availability": 7
                },
                "environmental_preferences": {
                    "temperature_min": 19.0,
                    "temperature_max": 22.0,
                    "co2_max": 700.0,
                    "sound_max": 45.0
                },
                "facility_requirements": {
                    "min_seating": 1
                },
                "requested_time": "2024-12-23T14:00:00Z",
                "duration_minutes": 120
            }
        },
        "example_2_lecture": {
            "description": "Need a large lecture room with projector",
            "request": {
                "criteria_weights": {
                    "temperature": 3,
                    "co2": 5,
                    "humidity": 1,
                    "sound": 5,
                    "facilities": 9,
                    "availability": 9
                },
                "environmental_preferences": {
                    "temperature_min": 18.0,
                    "temperature_max": 24.0,
                    "co2_max": 1000.0
                },
                "facility_requirements": {
                    "videoprojector": True,
                    "min_seating": 50
                },
                "requested_time": "2024-12-23T10:00:00Z",
                "duration_minutes": 90
            }
        },
        "example_3_computer_lab": {
            "description": "Need a computer lab with good ventilation",
            "request": {
                "criteria_weights": {
                    "temperature": 5,
                    "co2": 9,
                    "humidity": 3,
                    "sound": 3,
                    "facilities": 9,
                    "availability": 7
                },
                "environmental_preferences": {
                    "temperature_min": 19.0,
                    "temperature_max": 23.0,
                    "co2_max": 800.0
                },
                "facility_requirements": {
                    "computers": True,
                    "min_seating": 20
                },
                "requested_time": "2024-12-23T14:00:00Z",
                "duration_minutes": 180
            }
        }
    }
