from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import db
from app.routers import auth, sensors, facilities, calendar, ranking

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Connect to MongoDB, initialize indexes
    - Shutdown: Close MongoDB connection
    """
    # Startup
    logger.info("Starting IoT Room Selection API...")
    await db.connect()
    yield
    # Shutdown
    logger.info("Shutting down IoT Room Selection API...")
    await db.disconnect()


# FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    REST API for the IoT Room Selection Decision Support System.

    This API provides:
    - JWT authentication for admin access
    - Access to environmental sensor data (temperature, CO2, humidity, sound)
    - Room facilities information
    - University calendar availability
    - Multi-criteria room ranking using AHP (Analytic Hierarchy Process)

    Built for the University of Luxembourg IoT course project.
    """,
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS Middleware - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    sensors.router,
    prefix=f"{settings.API_V1_PREFIX}/sensors",
    tags=["Sensors"]
)
app.include_router(
    facilities.router,
    prefix=f"{settings.API_V1_PREFIX}/rooms",
    tags=["Rooms & Facilities"]
)
app.include_router(
    calendar.router,
    prefix=f"{settings.API_V1_PREFIX}/calendar",
    tags=["Calendar"]
)
app.include_router(
    ranking.router,
    prefix=f"{settings.API_V1_PREFIX}/rank",
    tags=["Decision Support"]
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "IoT Room Selection API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        await db.client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": settings.APP_VERSION
    }
