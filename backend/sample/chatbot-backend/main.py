import sys
import os
# Add the parent directory to the Python path to enable absolute imports
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules after environment is loaded
from src.cors_config import setup_cors
from src.qdrant_service import QdrantService
from src.utils.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend API",
    description="API for RAG Chatbot with book content search",
    version="1.0.0"
)

# Setup CORS as per spec T006
setup_cors(app)

# Initialize services
qdrant_service = QdrantService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up RAG Chatbot Backend...")

    # Initialize database connection
    try:
        await init_db()
        logger.info("Neon DB initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Neon DB: {e}")
        raise

    # Create Qdrant collection if it doesn't exist
    success = qdrant_service.create_collection()
    if success:
        logger.info("Qdrant collection ready")
    else:
        logger.error("Failed to create Qdrant collection")




@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "RAG Chatbot Backend is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Chatbot Backend",
        "version": "1.0.0"
    }

# Include API routes
from api import sessions, rag, ingestion, auth
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(rag.router, prefix="/api", tags=["rag"])
app.include_router(ingestion.router, prefix="/api", tags=["ingestion"])
app.include_router(auth.router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True
    )