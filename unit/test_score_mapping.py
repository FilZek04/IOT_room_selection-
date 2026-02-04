"""
Unit tests for score_mapping module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.ahp.score_mapping import (
    map_temperature,
    map_co2,
    map_humidity,
    map_light,
    map_noise,
    map_voc,
    map_air_quality,
    map_seating_capacity,
    map_equipment,
    map_av_facilities,
    get_mapping_function,
    TEMPERATURE_CONFIG,
    CO2_CONFIG,
)


class TestTemperatureMapping:
    """Tests for temperature mapping function."""
    
    def test_optimal_range_returns_one(self):
        """Test that optimal temperatures return 1.0."""
        assert map_temperature(22.0) == 1.0
        assert map_temperature(20.0) == 1.0
        assert map_temperature(24.0) == 1.0
    
    def test_acceptable_range_returns_above_half(self):
        """Test acceptable but not optimal returns > 0.5."""
        score_low = map_temperature(19.0)  # Below optimal, above acceptable
        score_high = map_temperature(25.0)  # Above optimal, below acceptable
        
        assert 0.5 < score_low < 1.0
        assert 0.5 < score_high < 1.0
    
    def test_outside_acceptable_returns_below_half(self):
        """Test values outside acceptable range return < 0.5."""
        score_cold = map_temperature(15.0)  # Too cold
        score_hot = map_temperature(30.0)  # Too hot
        
        assert score_cold < 0.5
        assert score_hot < 0.5
    
    def test_extreme_values_approach_zero(self):
        """Test extreme temperatures approach 0."""
        score_freezing = map_temperature(5.0)
        score_boiling = map_temperature(40.0)
        
        assert score_freezing < 0.3
        assert score_boiling < 0.3


class TestCO2Mapping:
    """Tests for CO2 mapping function."""
    
    def test_low_co2_returns_one(self):
        """Test that low CO2 returns 1.0."""
        assert map_co2(400) == 1.0
        assert map_co2(0) == 1.0
        assert map_co2(600) == 1.0
    
    def test_moderate_co2_returns_high_score(self):
        """Test moderate CO2 returns good score."""
        score = map_co2(800)
        assert 0.5 < score < 1.0
    
    def test_high_co2_returns_low_score(self):
        """Test high CO2 returns lower score."""
        score = map_co2(1200)
        assert score < 0.5
    
    def test_very_high_co2_approaches_zero(self):
        """Test very high CO2 approaches 0."""
        score = map_co2(2000)
        assert score < 0.3


class TestHumidityMapping:
    """Tests for humidity mapping function."""
    
    def test_optimal_humidity(self):
        """Test optimal humidity returns 1.0."""
        assert map_humidity(50) == 1.0
        assert map_humidity(40) == 1.0
        assert map_humidity(60) == 1.0
    
    def test_low_humidity(self):
        """Test low humidity returns reduced score."""
        score = map_humidity(35)  # Below optimal (40-60) but within acceptable (30-70)
        assert 0.5 < score < 1.0
    
    def test_high_humidity(self):
        """Test high humidity returns reduced score."""
        score = map_humidity(75)
        assert score < 1.0
    
    def test_extreme_humidity(self):
        """Test extreme humidity returns low score."""
        assert map_humidity(15) < 0.5
        assert map_humidity(90) < 0.5


class TestLightMapping:
    """Tests for light intensity mapping function."""
    
    def test_optimal_light(self):
        """Test optimal light returns 1.0."""
        assert map_light(400) == 1.0
        assert map_light(300) == 1.0
        assert map_light(500) == 1.0
    
    def test_dim_light(self):
        """Test dim light returns reduced score."""
        score = map_light(150)
        assert score < 1.0
    
    def test_bright_light(self):
        """Test too bright light returns reduced score."""
        score = map_light(800)
        assert score < 1.0


class TestNoiseMapping:
    """Tests for noise mapping function."""
    
    def test_quiet_returns_one(self):
        """Test quiet environment returns 1.0."""
        assert map_noise(30) == 1.0
        assert map_noise(20) == 1.0
        assert map_noise(0) == 1.0
    
    def test_moderate_noise(self):
        """Test moderate noise is acceptable."""
        score = map_noise(40)
        assert 0.5 < score < 1.0
    
    def test_loud_noise(self):
        """Test loud noise returns low score."""
        score = map_noise(55)
        assert score < 0.5


class TestVOCMapping:
    """Tests for VOC mapping function."""
    
    def test_low_voc_returns_one(self):
        """Test low VOC returns 1.0."""
        assert map_voc(100) == 1.0
        assert map_voc(0) == 1.0
    
    def test_high_voc_returns_low_score(self):
        """Test high VOC returns lower score."""
        score = map_voc(350)
        assert 0.5 < score < 1.0
    
    def test_very_high_voc(self):
        """Test very high VOC returns low score."""
        score = map_voc(600)
        assert score < 0.5


class TestAirQualityMapping:
    """Tests for AQI mapping function."""
    
    def test_good_aqi(self):
        """Test good AQI returns 1.0."""
        assert map_air_quality(30) == 1.0
        assert map_air_quality(50) == 1.0
    
    def test_moderate_aqi(self):
        """Test moderate AQI returns acceptable score."""
        score = map_air_quality(75)
        assert 0.5 < score < 1.0
    
    def test_poor_aqi(self):
        """Test poor AQI returns low score."""
        score = map_air_quality(150)
        assert score < 0.5


class TestSeatingCapacityMapping:
    """Tests for seating capacity mapping."""
    
    def test_exact_match(self):
        """Test exact match returns 1.0."""
        assert map_seating_capacity(30, 30) == 1.0
    
    def test_slight_oversize(self):
        """Test slight oversize is acceptable."""
        score = map_seating_capacity(40, 30)
        assert score == 1.0
    
    def test_undersize(self):
        """Test undersize returns reduced score."""
        score = map_seating_capacity(20, 30)
        assert score < 1.0
    
    def test_severely_undersize(self):
        """Test severely undersize returns low score."""
        score = map_seating_capacity(10, 30)
        assert score == 0.0
    
    def test_zero_required(self):
        """Test zero required returns 1.0 for any capacity."""
        assert map_seating_capacity(50, 0) == 1.0


class TestEquipmentMapping:
    """Tests for equipment mapping."""
    
    def test_not_required_not_present(self):
        """Test no requirement, no equipment returns 1.0."""
        assert map_equipment(False, 0, 0) == 1.0
    
    def test_not_required_present(self):
        """Test equipment present when not required is bonus."""
        assert map_equipment(True, 10, 0) == 1.0
    
    def test_required_and_present(self):
        """Test required and present returns 1.0."""
        assert map_equipment(True, 20, 15) == 1.0
    
    def test_required_but_missing(self):
        """Test required but missing returns 0."""
        assert map_equipment(False, 0, 10) == 0.0


class TestAVFacilitiesMapping:
    """Tests for A/V facilities mapping."""
    
    def test_not_required_not_present(self):
        """Test neither required nor present."""
        assert map_av_facilities(False, False) == 0.8
    
    def test_required_and_present(self):
        """Test required and present returns 1.0."""
        assert map_av_facilities(True, True) == 1.0
    
    def test_required_but_missing(self):
        """Test required but missing returns 0."""
        assert map_av_facilities(False, True) == 0.0
    
    def test_present_but_not_required(self):
        """Test bonus for having projector when not required."""
        assert map_av_facilities(True, False) == 1.0


class TestGetMappingFunction:
    """Tests for mapping function registry."""
    
    def test_valid_sensor_types(self):
        """Test all valid sensor types return functions."""
        valid_types = [
            "temperature", "co2", "humidity", 
            "light", "noise", "voc", "air_quality"
        ]
        
        for sensor_type in valid_types:
            func = get_mapping_function(sensor_type)
            assert callable(func)
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        func1 = get_mapping_function("Temperature")
        func2 = get_mapping_function("TEMPERATURE")
        func3 = get_mapping_function("temperature")
        
        # All should return same function
        assert func1(22) == func2(22) == func3(22)
    
    def test_invalid_sensor_type(self):
        """Test error for invalid sensor type."""
        with pytest.raises(ValueError):
            get_mapping_function("invalid_sensor")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
