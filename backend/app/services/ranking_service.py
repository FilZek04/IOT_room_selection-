from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import db
from app.models.ranking import (
    RankingRequest,
    RankedRoom,
    RankingResponse,
)
from app.models.calendar import EventStatus
from app.ahp import AHPEngine, UserRequirements

logger = logging.getLogger(__name__)


class RankingService:
    """Service for room ranking using AHP algorithm."""

    async def rank_rooms(self, request: RankingRequest) -> RankingResponse:
        """Rank rooms based on user preferences."""
        rooms = await self._fetch_all_rooms()

        if request.facility_requirements:
            rooms = self._filter_by_facilities(rooms, request.facility_requirements)

        if not rooms:
            return RankingResponse(
                ranked_rooms=[],
                total_rooms_evaluated=0,
                timestamp=datetime.utcnow(),
                request_summary=self._build_request_summary(request)
            )

        rooms_with_data = await self._enrich_with_sensor_data(rooms)

        if request.requested_time:
            rooms_with_data = await self._enrich_with_availability(
                rooms_with_data,
                request.requested_time,
                request.duration_minutes
            )

        ranked_rooms = await self._calculate_ahp_scores(
            rooms_with_data,
            request
        )

        ranked_rooms.sort(key=lambda x: x.overall_score, reverse=True)
        for idx, room in enumerate(ranked_rooms, start=1):
            room.rank = idx

        return RankingResponse(
            ranked_rooms=ranked_rooms,
            total_rooms_evaluated=len(ranked_rooms),
            timestamp=datetime.utcnow(),
            request_summary=self._build_request_summary(request)
        )

    async def _fetch_all_rooms(self) -> list[dict]:
        """Fetch all rooms from database."""
        collection = db.get_collection("rooms")
        cursor = collection.find({})
        return await cursor.to_list(length=100)

    def _filter_by_facilities(
        self,
        rooms: list[dict],
        requirements
    ) -> list[dict]:
        """Filter rooms based on facility requirements."""
        filtered = []

        for room in rooms:
            facilities = room["facilities"]

            if requirements.videoprojector is not None:
                if facilities.get("videoprojector", False) != requirements.videoprojector:
                    continue

            if requirements.min_seating is not None:
                if facilities.get("seating_capacity", 0) < requirements.min_seating:
                    continue

            if requirements.computers is not None:
                has_computers = facilities.get("computers", 0) > 0
                if has_computers != requirements.computers:
                    continue

            if requirements.min_training_robots is not None:
                if facilities.get("robots_for_training", 0) < requirements.min_training_robots:
                    continue

            if requirements.whiteboard is not None:
                if facilities.get("whiteboard", False) != requirements.whiteboard:
                    continue

            filtered.append(room)

        return filtered

    async def _enrich_with_sensor_data(self, rooms: list[dict]) -> list[dict]:
        """Enrich rooms with latest sensor readings."""
        sensor_collection = db.get_collection("sensor_readings")

        for room in rooms:
            room_name = room["name"]

            pipeline = [
                {"$match": {"room_name": room_name}},
                {"$sort": {"timestamp": -1}},
                {
                    "$group": {
                        "_id": "$sensor_type",
                        "recent_values": {"$push": "$value"},
                        "latest_timestamp": {"$first": "$timestamp"}
                    }
                },
                {
                    "$project": {
                        "sensor_type": "$_id",
                        "average": {"$avg": {"$slice": ["$recent_values", 10]}},
                        "latest_timestamp": 1
                    }
                }
            ]

            results = await sensor_collection.aggregate(pipeline).to_list(length=10)

            sensor_data = {}
            for doc in results:
                sensor_type = doc["sensor_type"]
                sensor_data[sensor_type] = {
                    "value": doc["average"],
                    "timestamp": doc["latest_timestamp"]
                }

            room["sensor_data"] = sensor_data

        return rooms

    async def _enrich_with_availability(
        self,
        rooms: list[dict],
        requested_time: datetime,
        duration_minutes: Optional[int]
    ) -> list[dict]:
        """Check calendar availability for each room."""
        calendar_collection = db.get_collection("calendar_events")

        end_time = requested_time
        if duration_minutes:
            end_time = requested_time + timedelta(minutes=duration_minutes)

        for room in rooms:
            room_name = room["name"]

            conflict = await calendar_collection.find_one({
                "room_name": room_name,
                "status": EventStatus.CONFIRMED.value,
                "$or": [
                    {
                        "start_time": {"$gte": requested_time, "$lt": end_time}
                    },
                    {
                        "end_time": {"$gt": requested_time, "$lte": end_time}
                    },
                    {
                        "start_time": {"$lte": requested_time},
                        "end_time": {"$gte": end_time}
                    }
                ]
            })

            room["is_available"] = conflict is None

        return rooms

    async def _calculate_ahp_scores(
        self,
        rooms: list[dict],
        request: RankingRequest,
    ) -> list[RankedRoom]:
        if not rooms:
            return []

        engine = AHPEngine()

        min_seating = 0
        if request.facility_requirements and request.facility_requirements.min_seating is not None:
            min_seating = int(request.facility_requirements.min_seating)

        requirements = UserRequirements(
            required_seats=min_seating,
            need_projector=bool(request.facility_requirements.videoprojector)
            if request.facility_requirements and request.facility_requirements.videoprojector is not None
            else False,
            need_computers=1 if request.facility_requirements and request.facility_requirements.computers else 0,
        )
        engine.set_requirements(requirements)

        def _build_comparisons_from_weights(
            criteria: list[str],
            weights_map: dict[str, float],
        ) -> dict[tuple, float]:
            comps: dict[tuple, float] = {}
            for i, a in enumerate(criteria):
                wa = max(float(weights_map.get(a, 1.0)), 0.001)
                for b in criteria[i + 1 :]:
                    wb = max(float(weights_map.get(b, 1.0)), 0.001)
                    ratio = wa / wb
                    comps[(a, b)] = min(max(ratio, 1 / 9), 9)
            return comps

        weights = request.criteria_weights

        comfort_weight = float(weights.temperature + weights.humidity + weights.sound)
        health_weight = float(weights.co2)
        usability_weight = float(weights.facilities)
        total_main = comfort_weight + health_weight + usability_weight
        if total_main == 0:
            comfort_weight = health_weight = usability_weight = 1.0
            total_main = 3.0

        main_weights = {
            "Comfort": comfort_weight / total_main,
            "Health": health_weight / total_main,
            "Usability": usability_weight / total_main,
        }

        main_comparisons = _build_comparisons_from_weights(
            ["Comfort", "Health", "Usability"],
            main_weights,
        )

        comfort_sub_weights = {
            "Temperature": float(weights.temperature),
            "Lighting": 1.0,
            "Noise": float(weights.sound),
            "Humidity": float(weights.humidity),
        }
        health_sub_weights = {
            "CO2": float(weights.co2),
            "AirQuality": 1.0,
            "VOC": 1.0,
        }
        usability_sub_weights = {
            "SeatingCapacity": float(weights.facilities),
            "Equipment": float(weights.facilities),
            "AVFacilities": float(weights.facilities),
        }

        sub_comparisons = {
            "Comfort": _build_comparisons_from_weights(
                ["Temperature", "Lighting", "Noise", "Humidity"],
                comfort_sub_weights,
            ),
            "Health": _build_comparisons_from_weights(
                ["CO2", "AirQuality", "VOC"],
                health_sub_weights,
            ),
            "Usability": _build_comparisons_from_weights(
                ["SeatingCapacity", "Equipment", "AVFacilities"],
                usability_sub_weights,
            ),
        }

        engine.set_user_preferences(
            main_comparisons=main_comparisons,
            sub_comparisons=sub_comparisons,
        )

        room_payloads = []
        for room in rooms:
            sensor_data = room.get("sensor_data", {}) or {}
            facilities = room.get("facilities", {}) or {}
            room_payloads.append(
                {
                    "room_id": room.get("id") or room.get("room_id") or room.get("name", ""),
                    "name": room.get("name") or room.get("room_id") or "",
                    "temperature": (sensor_data.get("temperature") or {}).get("value"),
                    "co2": (sensor_data.get("co2") or {}).get("value"),
                    "humidity": (sensor_data.get("humidity") or {}).get("value"),
                    "light": (sensor_data.get("light") or {}).get("value"),
                    "noise": (sensor_data.get("sound") or {}).get("value"),
                    "voc": (sensor_data.get("voc") or {}).get("value"),
                    "air_quality": (sensor_data.get("air_quality") or {}).get("value"),
                    "seating_capacity": facilities.get("seating_capacity", 0),
                    "has_projector": facilities.get("videoprojector", False),
                    "computers": facilities.get("computers", 0),
                    "has_robots": facilities.get("robots_for_training", 0),
                    "is_available": room.get("is_available", True),
                    "raw_facilities": facilities,
                    "raw_conditions": {k: v.get("value") for k, v in sensor_data.items()},
                }
            )

        engine.load_room_data_from_dict(room_payloads)

        ahp_result = engine.evaluate_rooms()

        availability_weight = float(weights.availability)
        total_weight_full = (
            float(weights.temperature)
            + float(weights.co2)
            + float(weights.humidity)
            + float(weights.sound)
            + float(weights.facilities)
            + availability_weight
        )
        availability_share = availability_weight / total_weight_full if total_weight_full else 0.0

        ranked_rooms: list[RankedRoom] = []
        for room_score in ahp_result.rankings:
            source = next((r for r in room_payloads if r["room_id"] == room_score.room_id), None)
            is_available = bool(source.get("is_available")) if source else True
            facilities = (source or {}).get("raw_facilities", {})
            current_conditions = (source or {}).get("raw_conditions", {}) or None

            blended_score = (
                room_score.final_score * (1 - availability_share)
                + (1.0 if is_available else 0.0) * availability_share
            )

            criterion_scores = {
                cs.criterion_id: round(cs.normalized_score, 3)
                for cs in room_score.criterion_scores
            }
            criterion_scores["availability"] = 1.0 if is_available else 0.0

            ranked_rooms.append(
                RankedRoom(
                    room_name=room_score.room_name,
                    rank=room_score.rank,
                    overall_score=round(blended_score, 3),
                    criteria_scores=criterion_scores,
                    current_conditions=current_conditions,
                    facilities=facilities,
                    is_available=is_available,
                )
            )

        ranked_rooms.sort(key=lambda r: r.overall_score, reverse=True)
        for idx, room in enumerate(ranked_rooms, start=1):
            room.rank = idx

        return ranked_rooms

    def _score_temperature(self, value: float, min_pref: float, max_pref: float) -> float:
        """Score temperature (1.0 = perfect, 0.0 = very bad)."""
        if min_pref <= value <= max_pref:
            return 1.0
        elif value < min_pref:
            deviation = min_pref - value
            return max(0.0, 1.0 - (deviation / 5.0))
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 5.0))

    def _score_co2(self, value: float, max_pref: float) -> float:
        """Score CO2 level (lower is better)."""
        if value <= max_pref:
            return 1.0
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / max_pref))

    def _score_humidity(self, value: float, min_pref: float, max_pref: float) -> float:
        """Score humidity (within range is best)."""
        if min_pref <= value <= max_pref:
            return 1.0
        elif value < min_pref:
            deviation = min_pref - value
            return max(0.0, 1.0 - (deviation / 20.0))
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 20.0))

    def _score_sound(self, value: float, max_pref: float) -> float:
        """Score sound level (lower is better)."""
        if value <= max_pref:
            return 1.0
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 30.0))

    def _score_facilities(self, facilities: dict, requirements) -> float:
        """Score facilities (1.0 if all requirements met, scaled down otherwise)."""
        score = 0.5

        if facilities.get("videoprojector", False):
            score += 0.1

        if facilities.get("computers", 0) > 0:
            score += 0.1

        if facilities.get("whiteboard", False):
            score += 0.1

        capacity = facilities.get("seating_capacity", 0)
        if capacity >= 50:
            score += 0.2
        elif capacity >= 30:
            score += 0.1

        return min(1.0, score)

    def _build_request_summary(self, request: RankingRequest) -> dict:
        """Build a summary of the user's request for the response."""
        weights = request.criteria_weights

        criteria_list = [
            ("temperature", weights.temperature),
            ("co2", weights.co2),
            ("humidity", weights.humidity),
            ("sound", weights.sound),
            ("facilities", weights.facilities),
            ("availability", weights.availability),
        ]
        criteria_list.sort(key=lambda x: x[1], reverse=True)
        top_criteria = [c[0] for c in criteria_list[:3]]

        return {
            "top_criteria": top_criteria,
            "facility_requirements": request.facility_requirements is not None,
            "environmental_preferences": request.environmental_preferences is not None,
            "time_specific": request.requested_time is not None
        }


ranking_service = RankingService()
