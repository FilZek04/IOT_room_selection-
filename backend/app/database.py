from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager using Motor."""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DB_NAME]

            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

            await self._create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    def get_collection(self, collection_name: str):
        """Get a MongoDB collection."""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database[collection_name]

    async def _create_indexes(self):
        """Create MongoDB indexes for optimized queries."""
        try:
            sensor_collection = self.get_collection("sensor_readings")
            await sensor_collection.create_index(
                [("room_name", 1), ("sensor_type", 1), ("timestamp", -1)],
                name="room_sensor_time_idx"
            )
            await sensor_collection.create_index(
                [("sensor_type", 1), ("timestamp", -1)],
                name="sensor_time_idx"
            )

            rooms_collection = self.get_collection("rooms")
            await rooms_collection.create_index(
                [("name", 1)],
                unique=True,
                name="room_name_unique_idx"
            )
            await rooms_collection.create_index(
                [("facilities.videoprojector", 1), ("facilities.seating_capacity", 1)],
                name="facilities_query_idx"
            )

            calendar_collection = self.get_collection("calendar_events")
            await calendar_collection.create_index(
                [("room_name", 1), ("start_time", 1), ("end_time", 1)],
                name="room_time_range_idx"
            )
            await calendar_collection.create_index(
                [("event_id", 1)],
                unique=True,
                sparse=True,
                name="event_id_unique_idx"
            )

            users_collection = self.get_collection("users")
            await users_collection.create_index(
                [("username", 1)],
                unique=True,
                name="username_unique_idx"
            )
            await users_collection.create_index(
                [("email", 1)],
                unique=True,
                sparse=True,
                name="email_unique_idx"
            )
            await users_collection.create_index(
                [("is_active", 1)],
                name="is_active_idx"
            )

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")


db = Database()
