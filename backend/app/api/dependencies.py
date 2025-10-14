"""
Database connection and operations
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.database = self.client[settings.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            logger.info("Connected to MongoDB successfully")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        # Ensure minimal initialization without scheduling background tasks
        if self.database is None:
            try:
                self.client = AsyncIOMotorClient(settings.mongodb_url)
                self.database = self.client[settings.database_name]
            except Exception:
                # Fallback to None; callers may have monkeypatched this instance in tests
                return None
        return self.database[collection_name]


# Global database instance
database = Database()

# Initialize connection on import
async def init_database():
    """Initialize database connection"""
    await database.connect()

# Dependency for FastAPI
async def get_database():
    """Get database instance for dependency injection"""
    if not database._connected:
        await database.connect()
    return database
