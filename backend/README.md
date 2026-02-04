# IoT Room Selection Backend

FastAPI-based REST API for the IoT Room Selection Decision Support System.

## Features

- **Sensor Data API** - Access temperature, CO2, humidity, sound, and other environmental data
- **Room Facilities API** - Query room capabilities (projectors, seating, computers, etc.)
- **Calendar Integration** - Check room availability via University calendar
- **AHP Ranking** - Multi-criteria decision support for room selection
- **Auto Documentation** - Swagger UI and ReDoc included
- **Docker Ready** - Easy deployment to Raspberry Pi

## Quick Start

### Option 1: Docker (Recommended)

```bash
# From project root directory
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access API documentation
open http://localhost:8000/docs
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start MongoDB (requires Docker)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Sensor Data
- `GET /api/v1/sensors/{room_id}/{sensor_type}` - Get sensor readings
- `GET /api/v1/sensors/{room_id}/{sensor_type}/stats` - Get aggregated statistics
- `GET /api/v1/sensors/{room_id}/latest` - Get latest readings for all sensors

### Rooms & Facilities
- `GET /api/v1/rooms/` - List all rooms
- `GET /api/v1/rooms/{room_id}` - Get room details
- `GET /api/v1/rooms/{room_id}/facilities` - Get room facilities

### Calendar
- `GET /api/v1/calendar/events` - Get calendar events
- `GET /api/v1/calendar/availability/{room_name}` - Check availability at time
- `GET /api/v1/calendar/availability/{room_name}/range` - Check availability for duration

### Decision Support (AHP Ranking)
- `POST /api/v1/rank` - Rank rooms based on preferences
- `GET /api/v1/rank/example` - Get example ranking requests

## Database Schema

See [docs/MONGODB_SCHEMA.md](../docs/MONGODB_SCHEMA.md) for detailed schema documentation.

**Collections:**
- `sensor_readings` - Time-series sensor data
- `rooms` - Room metadata and facilities
- `calendar_events` - Room bookings and availability

## Data Import

To import the mock sensor data:

```bash
# Create a data import script (see scripts/import_data.py)
python scripts/import_data.py
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic models
│   │   ├── sensor.py
│   │   ├── room.py
│   │   ├── calendar.py
│   │   └── ranking.py
│   ├── routers/             # API route handlers
│   │   ├── sensors.py
│   │   ├── facilities.py
│   │   ├── calendar.py
│   │   └── ranking.py
│   ├── services/            # Business logic
│   │   └── ranking_service.py
│   └── ahp/                 # AHP algorithm (from Fede)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── .env                    # Environment variables
└── README.md               # This file
```

## Configuration

Edit `.env` file to configure:

```bash
# Application
APP_NAME="IoT Room Selection API"
DEBUG=True

# MongoDB
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DB_NAME="iot_room_selection"

# JWT (optional)
JWT_SECRET_KEY="your-secret-key-here"
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
pylint app/
```

## Deployment to Raspberry Pi

### Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspbian/Raspberry Pi OS (64-bit)
- Docker and Docker Compose installed

### Steps

1. **Install Docker on Raspberry Pi:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Clone repository:**
```bash
git clone <repository-url>
cd iot-room-selection
```

3. **Configure environment:**
```bash
cd backend
cp .env.example .env
# Edit .env as needed
```

4. **Import data:**
```bash
# Import mock sensor data to MongoDB
python scripts/import_data.py
```

5. **Start services:**
```bash
cd ..
docker-compose up -d
```

6. **Verify:**
```bash
curl http://localhost:8000/health
```

### Resource Optimization for Raspberry Pi

The Docker setup is optimized for ARM architecture:
- Uses slim Python image
- Non-root user for security
- Health checks for monitoring
- Automatic restart on failure

## AHP Integration

The ranking algorithm uses the Analytic Hierarchy Process (AHP) for multi-criteria decision making.

**Current Implementation:**
- Basic weighted scoring system (placeholder)
- Ready for integration with Fede's AHP algorithm

**To integrate AHP:**
1. Place AHP implementation in `app/ahp/`
2. Update `app/services/ranking_service.py` to use AHP module
3. See `_calculate_ahp_scores()` method for integration point

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Change port in docker-compose.yml or .env
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Contributing

This is a university project. Team members:
- **Anthony** - Backend/Database
- **Fede** - Algorithm/Data
- **Filip** - Frontend/UI

## License

University of Luxembourg - IoT Course Project (BPINFOR-124)
