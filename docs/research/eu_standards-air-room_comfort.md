# EU Indoor Environmental Quality Standards Research

> **Reference Standards:**
> - **EN 16798-1:2019** - Energy performance of buildings - Ventilation for buildings - Part 1: Indoor environmental input parameters for design and assessment
> - **EN 12464-1:2021** - Light and lighting - Lighting of work places
> - **WHO Air Quality Guidelines 2021** - Global air quality guidelines for particulate matter

This document summarizes the recommended threshold values for indoor environmental quality (IEQ) categories, specifically focusing on **Category II (Normal Expectation)** which is the standard target for new buildings and renovations.

---

## 1. Thermal Environment (Temperature)

Based on operative temperature for office-like spaces (EN 16798-1:2019).

| Category | Season | Recommended Range (°C) | Description |
|----------|--------|------------------------|-------------|
| **I** (High) | Winter | 21.0 - 23.0 | Spaces occupied by very sensitive and fragile persons |
| **I** (High) | Summer | 23.5 - 25.5 | |
| **II** (Normal) | **Winter** | **20.0 - 24.0** | **New buildings and renovations (Standard)** |
| **II** (Normal) | **Summer** | **23.0 - 26.0** | |
| **III** (Moderate) | Winter | 19.0 - 25.0 | Existing buildings |
| **III** (Moderate) | Summer | 22.0 - 27.0 | |

> **Note:** "Summer" values typically assume cooling systems. For free-running (non-cooled) buildings, adaptive thermal comfort models apply.

---

## 2. Indoor Air Quality (CO2 & Ventilation)

CO2 levels are used as a proxy for ventilation adequacy (EN 16798-1:2019). The values below are **above outdoor concentration** (typically 400 ppm).

| Category | CO2 Above Outdoor (ppm) | Total CO2 Est. (ppm)* | Ventilation Rate per Person (l/s) |
|----------|-------------------------|-----------------------|-----------------------------------|
| I | 550 | < 950 | 10 |
| **II** | **800** | **< 1200** | **7** |
| III | 1350 | < 1750 | 4 |
| IV | > 1350 | > 1750 | < 4 |

*Assuming outdoor CO2 is approx. 400 ppm.

**For our system:** Optimal ≤ 800 ppm, Acceptable ≤ 1000 ppm (aligns with Cat II).

---

## 3. Humidity

Relative Humidity (RH) ranges for health and comfort (EN 16798-1:2019).

| Category | Design Dehumidification (Max) | Design Humidification (Min) |
|----------|-------------------------------|-----------------------------|
| I | 50% | 30% |
| **II** | **60%** | **25%** |
| III | 70% | 20% |

> **General Recommendation:** Keep between **30% - 60%** for optimal comfort and health.

---

## 4. Lighting (EN 12464-1:2021)

Reference: **EN 12464-1:2021** - Light and lighting - Lighting of work places.

| Type of Area | Lux (Illuminance) | UGR (Glare Limit) | Ra (Color Rendering) |
|--------------|-------------------|-------------------|----------------------|
| Classrooms/Tutorial rooms | 300 - 500 | 19 | 80 |
| Offices (Writing/Typing) | 500 | 19 | 80 |
| Meeting rooms | 500 | 19 | 80 |
| Corridors | 100 | 28 | 40 |

> **Target:** **300 - 500 Lux** for study/work areas.

---

## 5. Acoustics (Noise)

Reference: EN 16798-1:2019 & WHO Guidelines. Values are A-weighted equivalent sound pressure levels (L_Aeq).

| Category | Maximum Noise Level (dBA) |
|----------|---------------------------|
| I | 30 - 35 |
| **II** | **35 - 40** |
| III | 40 - 45 |

> **Target:** **< 35 dBA** for high comfort/learning environments; **< 40 dBA** for general office work.

---

## 6. Volatile Organic Compounds (VOCs)

EN 16798-1 focuses on ventilation rates; specific TVOC limits come from complementary standards (WELL Building Standard, German UBA).

| Contaminant | Optimal (ppb) | Acceptable (ppb) | Source |
|-------------|---------------|------------------|--------|
| Total VOCs | < 200 | < 400 | WELL Building Standard |
| Formaldehyde | < 80 | < 100 | WHO Guidelines |

---

## 7. Particulate Matter (PM2.5 & PM10) - WHO 2021

Reference: **WHO Global Air Quality Guidelines 2021** - These are the most stringent evidence-based guidelines for particulate matter.

### PM2.5 (Fine Particles ≤ 2.5 μm)

| Metric | WHO 2021 Guideline | Previous WHO 2005 |
|--------|-------------------|-------------------|
| Annual mean | **5 μg/m³** | 10 μg/m³ |
| 24-hour mean | **15 μg/m³** | 25 μg/m³ |

### PM10 (Coarse Particles ≤ 10 μm)

| Metric | WHO 2021 Guideline | Previous WHO 2005 |
|--------|-------------------|-------------------|
| Annual mean | **15 μg/m³** | 20 μg/m³ |
| 24-hour mean | **45 μg/m³** | 50 μg/m³ |

### Indoor Air Quality Categories for PM

| Category | PM2.5 (μg/m³) | PM10 (μg/m³) | Description |
|----------|---------------|--------------|-------------|
| Excellent | ≤ 5 | ≤ 15 | WHO annual guideline |
| Good | ≤ 15 | ≤ 45 | WHO 24-hour guideline |
| Acceptable | ≤ 35 | ≤ 75 | US EPA "Good" AQI threshold |
| Poor | > 35 | > 75 | Health risk increases |

> **For our system:** Optimal ≤ 15 μg/m³ PM2.5, ≤ 45 μg/m³ PM10 (WHO 24h guidelines).

---

## Summary of "Comfortable Room" Criteria (Category II)

For the Room Selection Algorithm, a "Comfortable Room" is defined as:

| Criterion | Optimal Range | Acceptable Range | Source |
|-----------|---------------|------------------|--------|
| **Temperature** | 20-24°C (winter) / 23-26°C (summer) | 18-27°C | EN 16798-1 Cat II |
| **CO2** | ≤ 800 ppm | ≤ 1000 ppm | EN 16798-1 Cat II |
| **Humidity** | 40-60% | 30-70% | EN 16798-1 |
| **Lighting** | 300-500 lux | 200-750 lux | EN 12464-1 |
| **Noise** | ≤ 35 dBA | ≤ 45 dBA | EN 16798-1 / WHO |
| **VOC** | ≤ 200 ppb | ≤ 400 ppb | WELL Standard |
| **PM2.5** | ≤ 15 μg/m³ | ≤ 35 μg/m³ | WHO 2021 |
| **PM10** | ≤ 45 μg/m³ | ≤ 75 μg/m³ | WHO 2021 |

---

## References

1. EN 16798-1:2019 - Energy performance of buildings - Ventilation for buildings
2. EN 12464-1:2021 - Light and lighting - Lighting of work places
3. WHO Global Air Quality Guidelines 2021 (ISBN 978-92-4-003422-8)
4. WELL Building Standard v2 - Air Quality
5. German Federal Environment Agency (UBA) - Indoor Air Hygiene Guidelines
