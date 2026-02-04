# IoT Room Selection Decision Support System

A smart room recommendation system using AHP algorithm, FastAPI, React, and MongoDB.

## Quick Links

- [Project Tracker (Gantt Chart)](https://filzek04.github.io/IOT_room_selection-/)
- [API Documentation (Swagger)](http://localhost:8000/docs) — run `docker-compose up` then open link
- [Grafana Dashboard](http://localhost:3000) — run `docker-compose --profile dev up` then open link (admin/admin123)

## Team

| Role | Member | Responsibilities |
|------|--------|------------------|
| Backend/Database | Anthony | FastAPI, MongoDB, REST APIs |
| Algorithm/Data | Fede | AHP implementation, EU standards research, JWT |
| Frontend/UI | Filip | React UI, Grafana dashboard, Hardware |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Protocols | I2C/Analog + MQTT + HTTP REST |
| Database | MongoDB |
| Backend | Python + FastAPI |
| Frontend | React + Vite |
| Monitoring | Grafana |
| Auth | JWT *(bonus)* |

## Project Structure

```
iot-room-selection/
├── docs/                          # Project tracker & documentation
│   ├── index.html                 # Gantt chart (GitHub Pages)
│   ├── tasks.json                 # Task data
│   ├── JWT_AUTHENTICATION.md      # JWT documentation
│   ├── AHP_TEST_REPORT.md         # AHP algorithm test results
│   └── project info&data/         # Research documents & sensor data
│       ├── AHP_Introduction.pdf
│       ├── IoT_project_ConfortRoom.pdf
│       └── Project_sensor_data/   # JSON sensor datasets
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── auth.py                # JWT authentication utilities
│   │   ├── config.py              # Application configuration
│   │   ├── database.py            # MongoDB connection
│   │   ├── routers/               # API Endpoints
│   │   │   ├── auth.py            # Authentication routes
│   │   │   ├── sensors.py         # Sensor data API
│   │   │   ├── facilities.py      # Room facilities API
│   │   │   ├── calendar.py        # Calendar/availability API
│   │   │   └── ranking.py         # AHP room ranking API
│   │   ├── models/                # Pydantic models
│   │   │   ├── user.py            # User/Token models
│   │   │   ├── sensor.py
│   │   │   ├── room.py
│   │   │   ├── calendar.py
│   │   │   └── ranking.py
│   │   ├── services/              # Business logic
│   │   │   └── ranking_service.py
│   │   └── ahp/                   # AHP algorithm implementation
│   │       ├── ahp_engine.py
│   │       ├── aggregation.py
│   │       ├── eigenvector.py
│   │       ├── pairwise_matrix.py
│   │       └── score_mapping.py
│   ├── scripts/
│   │   └── import_data.py         # Data import utility
│   ├── tests/                     # API tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/                      # React application
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── api/
│   │   │   ├── apiClient.js       # Axios API client with JWT
│   │   │   └── mockApi.js
│   │   ├── components/
│   │   │   ├── PreferenceMatrix.jsx
│   │   │   ├── ProfileAdjuster.jsx
│   │   │   ├── RoomRanking.jsx
│   │   │   ├── ScoreBreakdown.jsx
│   │   │   ├── SaatySlider.jsx
│   │   │   └── RangeSlider.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── RoomSelection.jsx
│   │   │   └── SwaggerDocs.jsx
│   │   ├── hooks/
│   │   │   └── useRoomRanking.js
│   │   ├── utils/
│   │   │   └── ahpCalculations.js
│   │   └── constants/
│   │       └── euStandards.js     # EU EN 16798-1 standards
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── grafana/                       # Grafana monitoring dashboards
│   ├── dashboards/
│   │   ├── room-monitoring.json
│   │   ├── facilities.json
│   │   └── alerts.json
│   ├── provisioning/
│   └── docker-compose_grafana.yml
├── unit/                          # AHP unit tests
│   ├── test_ahp_engine.py
│   ├── test_aggregation.py
│   ├── test_eigenvector.py
│   ├── test_pairwise_matrix.py
│   └── test_score_mapping.py
├── docker-compose.yml             # Main Docker stack
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (or Docker)
- Git

### Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/iot-room-selection.git
cd iot-room-selection

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Run Development
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Project Requirements

Based on course BPINFOR-124 (Introduction to IoT):

1. [x] Communication protocols specification (Comm A, B, C, D)
2. [x] Database design for sensor + facilities data
3. [x] Decision criteria based on EU standards (EN 16798-1)
4. [x] AHP algorithm for room ranking
5. [x] REST APIs with Swagger documentation
6. [x] UI1: End-user room selection interface
7. [x] UI2: Admin monitoring dashboard
8. [x] JWT authentication *(bonus)*


```bash
git add docs/tasks.json
git commit -m "Update task status: [task name] done"
git push
```

## License

MIT License - University of Luxembourg, 2024-2025
