from src.db.neon_service import neon_db_service
import asyncio
import logging

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the database connection pool"""
    try:
        await neon_db_service.initialize_pool()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db_service():
    """Get the database service instance"""
    return neon_db_service