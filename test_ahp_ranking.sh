#!/bin/bash

# AHP Room Ranking Algorithm Test Suite
# This script tests the room ranking API with different scenarios

BASE_URL="http://localhost:8000/api/v1"

echo "================================================"
echo "AHP Room Ranking Algorithm - Test Documentation"
echo "================================================"
echo ""

# Get room data summary first
echo "=== Current Room Data ==="
curl -s "${BASE_URL}/rooms" | python3 -m json.tool 2>/dev/null || echo "Rooms endpoint not available"
echo ""

# Test 1: Focused Work Scenario
echo "================================================"
echo "TEST 1: Focused Work Scenario"
echo "================================================"
echo "Requirements:"
echo "  - High importance on: Sound (9), CO2 (7), Availability (7)"
echo "  - Looking for: Quiet room, good air quality"
echo "  - Constraints: Temperature 19-22°C, CO2 < 700, Sound < 45 dB"
echo "  - Minimum seating: 1"
echo ""
echo "Expected Results:"
echo "  - Room_1 should rank high (good sound: 33 dB, good CO2: 605 ppm)"
echo "  - Room_4 should rank lower (bad sound: 63 dB)"
echo "  - Room_2 good candidate (low CO2: 510 ppm)"
echo ""

curl -X POST "${BASE_URL}/rank" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool > /tmp/test1_focused_work.json

cat /tmp/test1_focused_work.json
echo ""
echo ""

# Test 2: Lecture Scenario
echo "================================================"
echo "TEST 2: Lecture Scenario"
echo "================================================"
echo "Requirements:"
echo "  - High importance on: Facilities (9), Availability (9)"
echo "  - Looking for: Large room with projector"
echo "  - Constraints: Temperature 18-24°C, CO2 < 1000, min seating 50"
echo "  - Must have: videoprojector"
echo ""
echo "Expected Results:"
echo "  - Only Room_1 (62 seats) should qualify (min_seating: 50)"
echo "  - Rooms 2,3,4,5 filtered out (seating < 50)"
echo "  - Room_1 has projector: true"
echo ""

curl -X POST "${BASE_URL}/rank" \
  -H "Content-Type: application/json" \
  -d '{
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
      "videoprojector": true,
      "min_seating": 50
    },
    "requested_time": "2024-12-23T10:00:00Z",
    "duration_minutes": 90
  }' | python3 -m json.tool > /tmp/test2_lecture.json

cat /tmp/test2_lecture.json
echo ""
echo ""

# Test 3: Computer Lab Scenario
echo "================================================"
echo "TEST 3: Computer Lab Scenario"
echo "================================================"
echo "Requirements:"
echo "  - High importance on: Facilities (9), CO2 (9), Temperature (5)"
echo "  - Looking for: Computer lab with good ventilation"
echo "  - Constraints: Temperature 19-23°C, CO2 < 800, min seating 20"
echo "  - Must have: computers"
echo ""
echo "Expected Results:"
echo "  - Room_2, Room_3, Room_5 qualify (have computers)"
echo "  - Room_2: 20 computers, good CO2 (510 ppm)"
echo "  - Room_5: 25 computers, but higher CO2 (850 ppm)"
echo "  - Room_3: 10 computers, may be filtered out (seating 30 but computers only 10)"
echo ""

curl -X POST "${BASE_URL}/rank" \
  -H "Content-Type: application/json" \
  -d '{
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
      "computers": true,
      "min_seating": 20
    },
    "requested_time": "2024-12-23T14:00:00Z",
    "duration_minutes": 180
  }' | python3 -m json.tool > /tmp/test3_computer_lab.json

cat /tmp/test3_computer_lab.json
echo ""
echo ""

# Test 4: All Rooms Ranking (No Filters)
echo "================================================"
echo "TEST 4: All Rooms - No Filters"
echo "================================================"
echo "Requirements:"
echo "  - Balanced weights across all criteria"
echo "  - No facility requirements"
echo "  - No time restrictions"
echo ""
echo "Expected Results:"
echo "  - All 5 rooms should be ranked"
echo "  - Ranking based purely on environmental conditions and facilities"
echo ""

curl -X POST "${BASE_URL}/rank" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria_weights": {
      "temperature": 5,
      "co2": 5,
      "humidity": 5,
      "sound": 5,
      "facilities": 5,
      "availability": 5
    }
  }' | python3 -m json.tool > /tmp/test4_all_rooms.json

cat /tmp/test4_all_rooms.json
echo ""
echo ""

echo "================================================"
echo "TEST SUMMARY"
echo "================================================"
echo "Test results saved to:"
echo "  - /tmp/test1_focused_work.json"
echo "  - /tmp/test2_lecture.json"
echo "  - /tmp/test3_computer_lab.json"
echo "  - /tmp/test4_all_rooms.json"
echo ""
echo "To analyze results:"
echo "  cat /tmp/test1_focused_work.json | python3 -m json.tool"
echo ""
