"""
End-to-end unit tests for AHP Engine.

These tests use mock data similar to the actual project sensor data
to verify the complete AHP pipeline.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.ahp.ahp_engine import (
    AHPEngine,
    RoomData,
    UserRequirements,
    AHPResult,
)
from backend.app.ahp.aggregation import AggregationMethod


class TestAHPEngineInitialization:
    """Tests for AHP engine initialization."""
    
    def test_default_initialization(self):
        """Test engine initializes with valid defaults."""
        engine = AHPEngine()
        
        # Should have 3 main criteria
        assert len(engine._main_weights) == 3
        assert "Comfort" in engine._main_weights
        assert "Health" in engine._main_weights
        assert "Usability" in engine._main_weights
    
    def test_weights_sum_to_one(self):
        """Test that main weights sum to approximately 1."""
        engine = AHPEngine()
        
        total = sum(engine._main_weights.values())
        assert abs(total - 1.0) < 0.01
    
    def test_global_weights_calculated(self):
        """Test that global weights are calculated."""
        engine = AHPEngine()
        
        # Should have global weights for all sub-criteria
        assert len(engine._global_weights) > 0
        assert "Temperature" in engine._global_weights
        assert "CO2" in engine._global_weights
    
    def test_consistency_ratios_calculated(self):
        """Test that CRs are calculated for all matrices."""
        engine = AHPEngine()
        
        assert "main" in engine._consistency_ratios
        assert "Comfort" in engine._consistency_ratios
        assert "Health" in engine._consistency_ratios
        assert "Usability" in engine._consistency_ratios


class TestUserPreferences:
    """Tests for user preference adjustments."""
    
    def test_set_main_preferences(self):
        """Test adjusting main criteria preferences."""
        engine = AHPEngine()
        
        original_comfort = engine._main_weights["Comfort"]
        
        # Make Health much more important
        engine.set_user_preferences(
            main_comparisons={
                ("Health", "Comfort"): 5,
                ("Health", "Usability"): 7,
            }
        )
        
        # Health should now have higher weight
        assert engine._main_weights["Health"] > engine._main_weights["Comfort"]
    
    def test_set_sub_preferences(self):
        """Test adjusting sub-criteria preferences."""
        engine = AHPEngine()
        
        engine.set_user_preferences(
            sub_comparisons={
                "Comfort": {
                    ("Noise", "Temperature"): 5,  # Prioritize quiet over temp
                }
            }
        )
        
        # Noise should now be weighted higher within Comfort
        assert engine._sub_weights["Comfort"]["Noise"] > engine._sub_weights["Comfort"]["Temperature"]


class TestRoomDataLoading:
    """Tests for loading room data."""
    
    def test_load_room_data(self):
        """Test loading RoomData objects."""
        engine = AHPEngine()
        
        rooms = [
            RoomData(
                room_id="R1",
                room_name="Room 1",
                temperature=22.0,
                co2=600,
            ),
            RoomData(
                room_id="R2",
                room_name="Room 2",
                temperature=25.0,
                co2=900,
            ),
        ]
        
        engine.load_room_data(rooms)
        
        assert len(engine._rooms) == 2
    
    def test_load_room_data_from_dict(self):
        """Test loading room data from dictionary format."""
        engine = AHPEngine()
        
        rooms_data = [
            {
                "id": "R1",
                "name": "Room 1",
                "temperature": 22.0,
                "co2": 600,
                "seating_capacity": 30,
            },
            {
                "id": "R2",
                "name": "Room 2",
                "temperature": 25.0,
                "co2": 900,
                "seating_capacity": 20,
            },
        ]
        
        engine.load_room_data_from_dict(rooms_data)
        
        assert len(engine._rooms) == 2
        assert engine._rooms[0].temperature == 22.0

    def test_load_room_data_from_nested_facilities(self):
        """Test loading rooms with nested facilities block (matches project JSON)."""
        engine = AHPEngine()

        rooms_data = [
            {
                "room_id": "Room_1",
                "name": "Room 1",
                "temperature": 21.5,
                "co2": 550,
                "facilities": {
                    "videoprojector": True,
                    "seating_capacity": 62,
                    "computers": 20,
                    "robots_for_training": 5,
                },
            }
        ]

        engine.load_room_data_from_dict(rooms_data)

        room = engine._rooms[0]
        assert room.room_id == "Room_1"
        assert room.room_name == "Room 1"
        assert room.has_projector is True
        assert room.seating_capacity == 62
        assert room.computers == 20
        assert room.has_robots is True


class TestRoomEvaluation:
    """Tests for evaluating rooms."""
    
    def test_evaluate_single_room(self):
        """Test evaluating a single room."""
        engine = AHPEngine()
        
        rooms = [
            RoomData(
                room_id="R1",
                room_name="Room 1",
                temperature=22.0,
                co2=500,
                humidity=50,
                light=400,
                noise=30,
                voc=100,
                air_quality=30,
                seating_capacity=30,
                has_projector=True,
            )
        ]
        
        engine.load_room_data(rooms)
        result = engine.evaluate_rooms()
        
        assert len(result.rankings) == 1
        # This room has optimal values, should score high
        assert result.rankings[0].final_score > 0.8

    def test_raw_values_are_carried_into_scores(self):
        """Ensure raw sensor/facility values are preserved in criterion breakdown."""
        engine = AHPEngine()

        room = RoomData(
            room_id="R1",
            room_name="Room 1",
            temperature=22.0,
            co2=500,
            humidity=50,
            light=400,
            noise=30,
            voc=100,
            air_quality=30,
            seating_capacity=30,
            has_projector=True,
            computers=12,
        )

        engine.load_room_data([room])
        result = engine.evaluate_rooms()

        raw_values = {c.criterion_id: c.raw_value for c in result.rankings[0].criterion_scores}

        assert raw_values["Lighting"] == 400
        assert raw_values["Temperature"] == 22.0
        assert raw_values["SeatingCapacity"] == 30
        assert raw_values["Equipment"] == 12
        assert raw_values["AVFacilities"] is True
    
    def test_room_ranking_order(self):
        """Test that rooms are ranked correctly."""
        engine = AHPEngine()
        
        # Room 1: Good conditions
        # Room 2: Bad conditions
        rooms = [
            RoomData(
                room_id="R1",
                room_name="Good Room",
                temperature=22.0,
                co2=500,
                humidity=50,
                light=400,
                noise=30,
            ),
            RoomData(
                room_id="R2",
                room_name="Bad Room",
                temperature=35.0,  # Too hot
                co2=2000,  # High CO2
                humidity=90,  # Too humid
                light=50,  # Too dark
                noise=60,  # Loud
            ),
        ]
        
        engine.load_room_data(rooms)
        result = engine.evaluate_rooms()
        
        assert result.rankings[0].room_name == "Good Room"
        assert result.rankings[0].rank == 1
        assert result.rankings[1].room_name == "Bad Room"
        assert result.rankings[1].rank == 2
    
    def test_no_rooms_raises_error(self):
        """Test that evaluating with no rooms raises error."""
        engine = AHPEngine()
        
        with pytest.raises(ValueError):
            engine.evaluate_rooms()


class TestMockSensorData:
    """Tests using data similar to real sensor data files."""
    
    @pytest.fixture
    def mock_rooms(self):
        """Create mock rooms similar to actual project data."""
        return [
            RoomData(
                room_id="Room_1",
                room_name="Room 1",
                temperature=22.5,
                co2=650,
                humidity=45,
                light=380,
                noise=32,
                voc=150,
                air_quality=35,
                seating_capacity=62,
                has_projector=True,
            ),
            RoomData(
                room_id="Room_2",
                room_name="Room 2",
                temperature=24.0,
                co2=750,
                humidity=55,
                light=420,
                noise=38,
                voc=180,
                air_quality=42,
                seating_capacity=23,
                has_projector=True,
                computers=20,
            ),
            RoomData(
                room_id="Room_3",
                room_name="Room 3",
                temperature=23.0,
                co2=800,
                humidity=50,
                light=350,
                noise=40,
                voc=200,
                air_quality=48,
                seating_capacity=30,
                has_projector=True,
                computers=10,
            ),
            RoomData(
                room_id="Room_4",
                room_name="Room 4",
                temperature=26.5,  # Slightly warm
                co2=950,  # Higher CO2
                humidity=62,  # Slightly humid
                light=280,  # Dim
                noise=45,  # Noisy
                voc=250,
                air_quality=65,
                seating_capacity=12,
                has_projector=False,
            ),
            RoomData(
                room_id="Room_5",
                room_name="Room 5",
                temperature=21.5,
                co2=600,
                humidity=48,
                light=450,
                noise=28,
                voc=120,
                air_quality=30,
                seating_capacity=40,
                has_projector=True,
                computers=25,
            ),
        ]
    
    def test_evaluate_all_five_rooms(self, mock_rooms):
        """Test evaluating all 5 mock rooms."""
        engine = AHPEngine()
        engine.load_room_data(mock_rooms)
        
        result = engine.evaluate_rooms()
        
        assert len(result.rankings) == 5
        # All rooms should have valid scores
        for room in result.rankings:
            assert 0 <= room.final_score <= 1
    
    def test_best_room_is_room_5(self, mock_rooms):
        """Test that Room 5 ranks highest (best conditions)."""
        engine = AHPEngine()
        engine.load_room_data(mock_rooms)
        
        result = engine.evaluate_rooms()
        
        # Room 5 has best overall conditions
        assert result.rankings[0].room_id == "Room_5"
    
    def test_worst_room_is_room_4(self, mock_rooms):
        """Test that Room 4 ranks lowest (worst conditions)."""
        engine = AHPEngine()
        engine.load_room_data(mock_rooms)
        
        result = engine.evaluate_rooms()
        
        # Room 4 has worst conditions
        assert result.rankings[-1].room_id == "Room_4"
    
    def test_with_seating_requirement(self, mock_rooms):
        """Test ranking changes with seating requirements."""
        engine = AHPEngine()
        engine.load_room_data(mock_rooms)
        engine.set_requirements(UserRequirements(required_seats=50))
        
        result = engine.evaluate_rooms()
        
        # Rooms with more seats should score better on usability
        room_1 = next(r for r in result.rankings if r.room_id == "Room_1")
        room_4 = next(r for r in result.rankings if r.room_id == "Room_4")
        
        # Room 1 (62 seats) should have better usability than Room 4 (12 seats)
        assert room_1.usability_score > room_4.usability_score
    
    def test_with_projector_requirement(self, mock_rooms):
        """Test ranking with projector requirement."""
        engine = AHPEngine()
        engine.load_room_data(mock_rooms)
        engine.set_requirements(UserRequirements(need_projector=True))
        
        result = engine.evaluate_rooms()
        
        # Room 4 (no projector) should have lower usability
        room_4 = next(r for r in result.rankings if r.room_id == "Room_4")
        room_1 = next(r for r in result.rankings if r.room_id == "Room_1")
        
        assert room_1.usability_score > room_4.usability_score


class TestAggregationMethods:
    """Tests for different aggregation methods."""
    
    def test_weighted_sum_method(self):
        """Test weighted sum aggregation."""
        engine = AHPEngine()
        engine.load_room_data([
            RoomData(room_id="R1", room_name="R1", temperature=22.0, co2=500)
        ])
        
        result = engine.evaluate_rooms(method=AggregationMethod.WEIGHTED_SUM)
        
        assert len(result.rankings) == 1
    
    def test_weighted_product_method(self):
        """Test weighted product aggregation."""
        engine = AHPEngine()
        engine.load_room_data([
            RoomData(room_id="R1", room_name="R1", temperature=22.0, co2=500)
        ])
        
        result = engine.evaluate_rooms(method=AggregationMethod.WEIGHTED_PRODUCT)
        
        assert len(result.rankings) == 1
    
    def test_combined_method(self):
        """Test combined aggregation method."""
        engine = AHPEngine()
        engine.load_room_data([
            RoomData(room_id="R1", room_name="R1", temperature=22.0, co2=500)
        ])
        
        result = engine.evaluate_rooms(method=AggregationMethod.COMBINED)
        
        assert len(result.rankings) == 1


class TestConsistencyValidation:
    """Tests for AHP consistency validation."""
    
    def test_default_matrices_are_consistent(self):
        """Test that default matrices pass consistency check."""
        engine = AHPEngine()
        
        assert engine._is_consistent
        
        for name, cr in engine._consistency_ratios.items():
            assert cr < 0.1, f"Matrix '{name}' has CR={cr} >= 0.1"
    
    def test_result_includes_consistency_info(self):
        """Test that result includes consistency information."""
        engine = AHPEngine()
        engine.load_room_data([
            RoomData(room_id="R1", room_name="R1", temperature=22.0)
        ])
        
        result = engine.evaluate_rooms()
        
        assert hasattr(result, "is_consistent")
        assert hasattr(result, "consistency_ratios")


class TestWeightsSummary:
    """Tests for weights summary output."""
    
    def test_weights_summary_format(self):
        """Test that weights summary is formatted correctly."""
        engine = AHPEngine()
        
        summary = engine.get_weights_summary()
        
        assert "MAIN CRITERIA" in summary
        assert "SUB-CRITERIA" in summary
        assert "CONSISTENCY RATIOS" in summary
        assert "Comfort" in summary
        assert "Health" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
