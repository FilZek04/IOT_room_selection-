"""
Integration tests for API endpoints.
"""
import pytest
from datetime import datetime


class TestRootEndpoints:
    """Test root and health endpoints."""

    @pytest.mark.asyncio
    async def test_root(self, client):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "operational"

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestSensorEndpoints:
    """Test sensor data endpoints."""

    @pytest.mark.asyncio
    async def test_get_sensor_readings(self, client):
        """Test getting sensor readings for a room."""
        response = await client.get(
            "/api/v1/sensors/Room_1/temperature",
            params={"limit": 5}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["room_name"] == "Room_1"
        assert data["sensor_type"] == "temperature"
        assert data["unit"] == "°C"
        assert len(data["readings"]) <= 5
        assert "average" in data
        assert "min_value" in data
        assert "max_value" in data

    @pytest.mark.asyncio
    async def test_get_sensor_stats(self, client):
        """Test getting aggregated sensor statistics."""
        response = await client.get(
            "/api/v1/sensors/Room_1/temperature/stats"
        )
        assert response.status_code == 200
        data = response.json()

        assert data["room_name"] == "Room_1"
        assert data["sensor_type"] == "temperature"
        assert "average" in data
        assert "min_value" in data
        assert "max_value" in data
        assert "sample_count" in data
        assert data["sample_count"] > 0

    @pytest.mark.asyncio
    async def test_get_latest_readings(self, client):
        """Test getting latest readings for all sensors."""
        response = await client.get("/api/v1/sensors/Room_1/latest")
        assert response.status_code == 200
        data = response.json()

        assert data["room_name"] == "Room_1"
        assert "readings" in data
        assert "temperature" in data["readings"]
        assert "co2" in data["readings"]

    @pytest.mark.asyncio
    async def test_sensor_not_found(self, client):
        """Test 404 when room or sensor type not found."""
        response = await client.get("/api/v1/sensors/NonExistentRoom/temperature")
        assert response.status_code == 404


class TestRoomEndpoints:
    """Test room and facilities endpoints."""

    @pytest.mark.asyncio
    async def test_list_rooms(self, client):
        """Test listing all rooms."""
        response = await client.get("/api/v1/rooms/")
        assert response.status_code == 200
        data = response.json()

        assert "rooms" in data
        assert "total" in data
        assert data["total"] >= 3
        assert any(room["name"] == "Room_1" for room in data["rooms"])

    @pytest.mark.asyncio
    async def test_list_rooms_with_filters(self, client):
        """Test listing rooms with facility filters."""
        response = await client.get(
            "/api/v1/rooms/",
            params={"videoprojector": True, "min_seating": 30}
        )
        assert response.status_code == 200
        data = response.json()

        # Should only return rooms with projector and >= 30 seats
        for room in data["rooms"]:
            assert room["facilities"]["videoprojector"] is True
            assert room["facilities"]["seating_capacity"] >= 30

    @pytest.mark.asyncio
    async def test_get_room(self, client):
        """Test getting a specific room."""
        response = await client.get("/api/v1/rooms/Room_1")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Room_1"
        assert "facilities" in data
        assert data["facilities"]["videoprojector"] is True
        assert data["facilities"]["seating_capacity"] == 62

    @pytest.mark.asyncio
    async def test_get_room_with_conditions(self, client):
        """Test getting room with current environmental conditions."""
        response = await client.get(
            "/api/v1/rooms/Room_1",
            params={"include_conditions": True}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Room_1"
        assert "current_conditions" in data
        # Should have sensor data
        if data["current_conditions"]:
            assert "temperature" in data["current_conditions"]

    @pytest.mark.asyncio
    async def test_get_room_facilities(self, client):
        """Test getting only room facilities."""
        response = await client.get("/api/v1/rooms/Room_1/facilities")
        assert response.status_code == 200
        data = response.json()

        assert "videoprojector" in data
        assert "seating_capacity" in data
        assert data["videoprojector"] is True

    @pytest.mark.asyncio
    async def test_room_not_found(self, client):
        """Test 404 when room doesn't exist."""
        response = await client.get("/api/v1/rooms/NonExistentRoom")
        assert response.status_code == 404


class TestCalendarEndpoints:
    """Test calendar and availability endpoints."""

    @pytest.mark.asyncio
    async def test_get_events(self, client):
        """Test getting calendar events."""
        response = await client.get("/api/v1/calendar/events")
        assert response.status_code == 200
        data = response.json()

        assert "events" in data
        assert "total" in data
        assert data["total"] >= 2

    @pytest.mark.asyncio
    async def test_get_events_filtered_by_room(self, client):
        """Test getting events filtered by room."""
        response = await client.get(
            "/api/v1/calendar/events",
            params={"room_name": "Room_1"}
        )
        assert response.status_code == 200
        data = response.json()

        # All events should be for Room_1
        for event in data["events"]:
            assert event["room_name"] == "Room_1"

    @pytest.mark.asyncio
    async def test_check_availability(self, client):
        """Test checking room availability at a specific time."""
        # Check availability in 30 minutes (should be free)
        future_time = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        future_time = future_time.replace("+00:00", "Z")

        response = await client.get(
            "/api/v1/calendar/availability/Room_3",
            params={"requested_time": future_time}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["room_name"] == "Room_3"
        assert "is_available" in data
        assert isinstance(data["is_available"], bool)

    @pytest.mark.asyncio
    async def test_check_availability_range(self, client):
        """Test checking availability for a time range."""
        start_time = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        response = await client.get(
            "/api/v1/calendar/availability/Room_3/range",
            params={
                "start_time": start_time,
                "duration_minutes": 60
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["room_name"] == "Room_3"
        assert "is_available" in data
        assert "conflicting_events" in data


class TestRankingEndpoint:
    """Test room ranking endpoint."""

    @pytest.mark.asyncio
    async def test_rank_rooms_basic(self, client):
        """Test basic room ranking request."""
        request_data = {
            "criteria_weights": {
                "temperature": 5,
                "co2": 7,
                "humidity": 3,
                "sound": 5,
                "facilities": 9,
                "availability": 9
            }
        }

        response = await client.post("/api/v1/rank", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert "ranked_rooms" in data
        assert "total_rooms_evaluated" in data
        assert data["total_rooms_evaluated"] >= 3

        # Check that rooms are ranked (rank field present)
        for room in data["ranked_rooms"]:
            assert "rank" in room
            assert "overall_score" in room
            assert "criteria_scores" in room
            assert 0 <= room["overall_score"] <= 1

        # Check that ranks are sequential starting from 1
        ranks = [room["rank"] for room in data["ranked_rooms"]]
        assert ranks == list(range(1, len(ranks) + 1))

    @pytest.mark.asyncio
    async def test_rank_rooms_with_preferences(self, client):
        """Test ranking with environmental preferences."""
        request_data = {
            "criteria_weights": {
                "temperature": 9,
                "co2": 9,
                "humidity": 5,
                "sound": 3,
                "facilities": 5,
                "availability": 7
            },
            "environmental_preferences": {
                "temperature_min": 19.0,
                "temperature_max": 22.0,
                "co2_max": 800.0,
                "humidity_min": 40.0,
                "humidity_max": 60.0
            }
        }

        response = await client.post("/api/v1/rank", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert len(data["ranked_rooms"]) > 0
        # Rooms should have current_conditions
        for room in data["ranked_rooms"]:
            assert "current_conditions" in room

    @pytest.mark.asyncio
    async def test_rank_rooms_with_facility_requirements(self, client):
        """Test ranking with facility requirements."""
        request_data = {
            "criteria_weights": {
                "temperature": 5,
                "co2": 5,
                "humidity": 3,
                "sound": 3,
                "facilities": 9,
                "availability": 9
            },
            "facility_requirements": {
                "videoprojector": True,
                "min_seating": 30
            }
        }

        response = await client.post("/api/v1/rank", json=request_data)
        assert response.status_code == 200
        data = response.json()

        # All returned rooms should meet facility requirements
        for room in data["ranked_rooms"]:
            assert room["facilities"]["videoprojector"] is True
            assert room["facilities"]["seating_capacity"] >= 30

    @pytest.mark.asyncio
    async def test_rank_rooms_invalid_weights(self, client):
        """Test that invalid Saaty scale weights are rejected."""
        request_data = {
            "criteria_weights": {
                "temperature": 2,  # Invalid - not in Saaty scale (1, 3, 5, 7, 9)
                "co2": 5,
                "humidity": 3,
                "sound": 5,
                "facilities": 9,
                "availability": 9
            }
        }

        response = await client.post("/api/v1/rank", json=request_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_ranking_examples(self, client):
        """Test getting example ranking requests."""
        response = await client.get("/api/v1/rank/example")
        assert response.status_code == 200
        data = response.json()

        # Should have example scenarios
        assert "example_1_focused_work" in data
        assert "example_2_lecture" in data
        assert "example_3_computer_lab" in data
