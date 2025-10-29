from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.database.mongodb import mongodb
from app.routes import user_routes
from app.routes import voice

app.include_router(voice.router, prefix="/voice", tags=["Voice Analysis"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting up...")
    try:
        await mongodb.connect_to_database()
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

    yield


    logger.info("Shutting down...")
    await mongodb.close_database_connection()
    logger.info("MongoDB connection closed")


app = FastAPI(
    title="LinguaMentor API",
    description="Intelligent Language Tutor - Backend API",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(
    user_routes.router,
    prefix="/users",
    tags=["users"]
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to LinguaMentor API",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "MongoDB connected" if mongodb.client else "MongoDB disconnected"
    }


@app.get("/info")
async def api_info():
    return {
        "name": "LinguaMentor API",
        "description": "Intelligent Language Tutor Backend",
        "version": "1.0.0",
        "database": "MongoDB with Beanie ODM",
        "message_queue": "RabbitMQ",
        "features": [
            "User Management",
            "Language Learning",
            "Progress Tracking"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )