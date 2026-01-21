"""
MongoDB database connection and management.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from utils.logger import get_logger
from typing import Optional

logger = get_logger("MONGO_DB")

# MongoDB Configuration
MONGO_URL = "mongodb://localhost:27017"
MONGO_DB_NAME = "tradestat"
MONGO_TIMEOUT = 5000  # 5 seconds


class MongoDatabase:
    """MongoDB connection manager"""
    
    _instance: Optional['MongoDatabase'] = None
    
    def __init__(self, mongo_url: str = MONGO_URL, db_name: str = MONGO_DB_NAME):
        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=MONGO_TIMEOUT)
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            logger.info(f"✓ Connected to MongoDB: {db_name}")
            self._setup_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"✗ Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _setup_indexes(self):
        """Create indexes for better query performance"""
        try:
            # HS Code collection indexes
            self.db.hs_codes.create_index("hs_code", unique=True)
            self.db.hs_codes.create_index("trade_mode")
            self.db.hs_codes.create_index("scraped_at_ist")
            self.db.hs_codes.create_index("metadata.data_completeness_percent")
            
            # Partner countries collection indexes
            self.db.partner_countries.create_index([("hs_code", 1), ("country", 1)])
            self.db.partner_countries.create_index("country")
            
            logger.info("✓ Indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    @classmethod
    def get_instance(cls) -> 'MongoDatabase':
        """Get or create singleton instance"""
        if cls._instance is None:
            cls._instance = MongoDatabase()
        return cls._instance
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("✓ MongoDB connection closed")
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database instance
db: Optional[MongoDatabase] = None


def init_db(mongo_url: str = MONGO_URL, db_name: str = MONGO_DB_NAME) -> MongoDatabase:
    """Initialize database connection"""
    global db
    db = MongoDatabase(mongo_url, db_name)
    return db


def get_db() -> MongoDatabase:
    """Get database instance"""
    global db
    if db is None:
        db = MongoDatabase.get_instance()
    return db


def close_db():
    """Close database connection"""
    global db
    if db:
        db.close()
        db = None
