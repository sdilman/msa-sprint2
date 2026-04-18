from fastapi import FastAPI
from contextlib import asynccontextmanager
from kafka_consumer import stats_collector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Kafka consumer
    logger.info("Starting booking-history-service...")
    stats_collector.start()
    yield
    # Shutdown: Stop Kafka consumer
    logger.info("Shutting down booking-history-service...")
    stats_collector.stop()


app = FastAPI(
    title="Booking History Service",
    description="Service for collecting booking statistics from Kafka",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "service": "booking-history-service",
        "status": "running",
        "endpoints": ["/get_booking_stats", "/health"]
    }


@app.get("/get_booking_stats")
async def get_booking_stats():
    """
    Get booking statistics from Kafka events
    
    Returns:
        - by_user: Count of bookings per user_id
        - by_hotel: Count of bookings per hotel_id
        - by_date: Count of bookings per date
        - total_events: Total number of processed events
    """
    stats = stats_collector.get_stats()
    return stats


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/reset_stats")
async def reset_stats():
    """Reset statistics (for testing purposes)"""
    stats_collector.reset_stats()
    return {"message": "Statistics reset successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)