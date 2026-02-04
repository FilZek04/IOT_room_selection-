# Criteria Hierarchy Design

> **Design document for the AHP criteria hierarchy used in the IoT Room Selection system.**

## Two-Phase Decision Process

The system uses a **two-phase approach** combining hard constraints with AHP scoring:

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: FACILITY REQUIREMENTS (Hard Constraints)          │
│                                                             │
│  User specifies MUST-HAVE requirements:                     │
│  • Minimum seats (e.g., 25 for a class)                     │
│  • Require projector (yes/no)                               │
│  • Require computers (yes/no)                               │
│                                                             │
│  → Rooms not meeting requirements are FILTERED OUT          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: AHP SCORING (On qualifying rooms only)            │
│                                                             │
│  Ranks remaining rooms based on:                            │
│  • Comfort (40%) - Temperature, Lighting, Noise, Humidity   │
│  • Health (35%) - CO2, Air Quality, VOC, PM2.5, PM10        │
│  • Usability (25%) - Seating, Equipment, A/V                │
│                                                             │
│  → Returns ranked list ordered by overall AHP score         │
└─────────────────────────────────────────────────────────────┘
```

### Why Two Phases?

| Aspect | Hard Constraints (Phase 1) | AHP Scoring (Phase 2) |
|--------|---------------------------|----------------------|
| **Purpose** | Eliminate unsuitable rooms | Rank remaining rooms |
| **User Input** | Simple values (numbers, checkboxes) | Pairwise comparisons |
| **Logic** | Pass/Fail | Weighted scoring |
| **Example** | "Must have ≥ 25 seats" | "Temperature is more important than noise" |

This approach is standard in Multi-Criteria Decision Making (MCDM) literature and doesn't violate AHP axioms.

---

## Hierarchy Structure

```
Select Best Room (Goal)
├─ Comfort (40%)
│  ├─ Temperature
│  ├─ Lighting
│  ├─ Noise
│  └─ Humidity
├─ Health (35%)
│  ├─ CO2
│  ├─ Air Quality (AQI)
│  ├─ VOC
│  ├─ PM2.5
│  └─ PM10
└─ Usability (25%)
   ├─ Seating Capacity
   ├─ Equipment (computers)
   └─ A/V Facilities (projector)
```

Each leaf node maps directly to the inputs expected by `AHPEngine.SUB_CRITERIA`, ensuring
the documentation stays in sync with the FastAPI backend module.

---

## Main Criteria Weights

| Criterion | Default Weight | Justification |
|-----------|----------------|---------------|
| **Comfort** | 40% | Physical comfort directly impacts productivity and satisfaction |
| **Health** | 35% | Poor air quality impairs cognitive function (studies show 15-50% decline) |
| **Usability** | 25% | Must meet basic functional requirements |

---

## Sub-Criteria Details

### Comfort (40%)

| Sub-Criterion | Local Weight | Global Weight | Data Source | Standard |
|---------------|--------------|---------------|-------------|----------|
| Temperature | 35% | 14.0% | `temperature_sensor_data.json` | EN 16798-1 |
| Lighting | 25% | 10.0% | `LightIntensity_sensor_data.json` | EN 12464-1 |
| Noise | 25% | 10.0% | `sound_sensor_data.json` | EN 16798-1 |
| Humidity | 15% | 6.0% | `humidity_sensor_data.json` | EN 16798-1 |

### Health (35%)

| Sub-Criterion | Local Weight | Global Weight | Data Source | Standard |
|---------------|--------------|---------------|-------------|----------|
| CO2 Level | 40% | 14.0% | `co2_sensor_data.json` | EN 16798-1 |
| Air Quality | 20% | 7.0% | `air_quality_sensor_data.json` | US EPA AQI |
| VOC | 15% | 5.25% | `voc_sensor_data.json` | WELL Standard |
| PM2.5 | 15% | 5.25% | `air_quality_sensor_data.json` | WHO 2021 |
| PM10 | 10% | 3.5% | `air_quality_sensor_data.json` | WHO 2021 |

### Usability (25%)

| Sub-Criterion | Local Weight | Global Weight | Data Source |
|---------------|--------------|---------------|-------------|
| Seating Capacity | 33% | 8.3% | `room_facilities_data.json` |
| Equipment | 33% | 8.3% | `room_facilities_data.json` |
| A/V Facilities | 33% | 8.3% | `room_facilities_data.json` |

> **Note:** Usability sub-criteria use equal weights because hard facility requirements 
> (minimum seats, require projector, require computers) are handled as pre-filters in Phase 1.
> AHP scoring only applies to rooms that already meet all requirements.

---

## Threshold Values Summary

### Comfort Criteria

| Criterion | Optimal Range | Acceptable Range | Unit | Source |
|-----------|---------------|------------------|------|--------|
| Temperature (Winter) | 20-24°C | 18-27°C | °C | EN 16798-1 Cat II |
| Temperature (Summer) | 23-26°C | 18-27°C | °C | EN 16798-1 Cat II |
| Lighting | 300-500 | 200-750 | lux | EN 12464-1 |
| Noise | 0-35 | 0-45 | dBA | EN 16798-1 / WHO |
| Humidity | 40-60 | 30-70 | % | EN 16798-1 |

### Health Criteria

| Criterion | Optimal Range | Acceptable Range | Unit | Source |
|-----------|---------------|------------------|------|--------|
| CO2 | 400-800 | 400-1000 | ppm | EN 16798-1 Cat II |
| Air Quality | 0-50 | 0-100 | AQI | US EPA |
| VOC | 0-200 | 0-400 | ppb | WELL Standard |
| PM2.5 | 0-15 | 0-35 | μg/m³ | WHO 2021 |
| PM10 | 0-45 | 0-75 | μg/m³ | WHO 2021 |

---

## Pairwise Comparison Matrices

### Main Criteria Matrix

```
            Comfort  Health  Usability
Comfort   [   1      1.2     2.0   ]
Health    [  0.83    1       1.5   ]
Usability [  0.5    0.67     1     ]
```
CR = 0.003 ✓

### Comfort Sub-Criteria Matrix

```
              Temp   Light   Noise   Humidity
Temperature [  1      2       2        3     ]
Lighting    [ 0.5     1       1        2     ]
Noise       [ 0.5     1       1        2     ]
Humidity    [ 0.33   0.5     0.5       1     ]
```
CR = 0.008 ✓

### Health Sub-Criteria Matrix

```
               CO2    AirQuality   VOC    PM2.5   PM10
CO2         [  1        2          3       3       4    ]
AirQuality  [ 0.5       1          1.5     1.5     2    ]
VOC         [ 0.33     0.67        1       1       1.5  ]
PM2.5       [ 0.33     0.67        1       1       1.5  ]
PM10        [ 0.25     0.5        0.67    0.67     1    ]
```
CR = 0.006 ✓

### Usability Sub-Criteria Matrix

```
                 Seating   Equipment   A/V
SeatingCapacity [   1         1         1   ]
Equipment       [   1         1         1   ]
AVFacilities    [   1         1         1   ]
```
CR = 0.000 ✓ (Equal weights)

> **Note:** Sub-criteria receive equal weights because hard facility requirements 
> are handled as pre-filters before AHP scoring.

---

## User Customization

Users can adjust weights via pairwise comparisons using the Saaty 1-9 scale:

| Preference Statement | Saaty Value |
|---------------------|-------------|
| "Temperature is equally important as Lighting" | 1 |
| "Health is moderately more important than Comfort" | 3 |
| "Noise is much more important than Humidity" | 5 |
| "CO2 is extremely more important than VOC" | 9 |

Example UI adjustment:
```
"How much more important is Health compared to Comfort?"
[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]
  ↑                 ↑                             ↑
Equal          Moderate                      Extreme
```

---

## Facility Requirements (Hard Constraints)

Before AHP scoring begins, users can specify **hard requirements** that filter out unsuitable rooms.

### Available Constraints

| Constraint | Input Type | Behavior |
|------------|------------|----------|
| **Minimum Seats** | Number (0-500) | Rooms with `seating_capacity < value` are excluded |
| **Require Projector** | Checkbox | If checked, rooms without `videoprojector=true` are excluded |
| **Require Computers** | Checkbox | If checked, rooms with `computers=0` are excluded |

### Example Scenarios

**Scenario 1: Lecture for 30 students**
```
Minimum Seats: 30
Require Projector: ✓
Require Computers: ☐
```
→ Only rooms with ≥30 seats AND a projector proceed to AHP ranking

**Scenario 2: Computer lab session**
```
Minimum Seats: 20
Require Projector: ☐
Require Computers: ✓
```
→ Only rooms with ≥20 seats AND computers proceed to AHP ranking

**Scenario 3: Small meeting (no special requirements)**
```
Minimum Seats: (empty)
Require Projector: ☐
Require Computers: ☐
```
→ All rooms proceed to AHP ranking

### Why Hard Constraints Instead of Weighted Preferences?

| Approach | Problem |
|----------|---------|
| Weighted (e.g., "Seating is 5× more important than projector") | Ambiguous - a room with 100 seats might still rank higher than one with 25 seats even if you need exactly 25 |
| Hard Constraints (e.g., "I need minimum 25 seats") | Clear - rooms with <25 seats are simply not shown |

Hard constraints are more intuitive for functional requirements where there's a clear pass/fail criterion.
