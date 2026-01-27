import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.endpoints import domains, monitoring, scheduler
from src.core.config import settings
from src.db.repository import repository
from src.scheduler.scheduler import monitoring_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    await repository.connect()

    # Start scheduler if enabled
    if settings.ENABLE_SCHEDULER:
        monitoring_scheduler.start()
        logger.info("Background scheduler started")
    else:
        logger.info("Background scheduler is disabled")

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Stop scheduler
    if settings.ENABLE_SCHEDULER:
        monitoring_scheduler.shutdown(wait=True)
        logger.info("Scheduler shutdown complete")

    await repository.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional subdomain monitoring API with automated scheduling",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domains.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(scheduler.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "scheduler_enabled": settings.ENABLE_SCHEDULER,
        "scheduler_running": (
            monitoring_scheduler.is_running if settings.ENABLE_SCHEDULER else False
        ),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await repository.count()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "scheduler_enabled": settings.ENABLE_SCHEDULER,
        "scheduler_running": (
            monitoring_scheduler.is_running if settings.ENABLE_SCHEDULER else False
        ),
    }
