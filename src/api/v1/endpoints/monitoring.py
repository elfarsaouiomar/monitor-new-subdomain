import logging

from fastapi import APIRouter, Depends

from src.api.dependencies import get_monitoring_service, get_repository
from src.db.repository import MongoRepository
from src.models.domain import MonitoringStats
from src.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/check-all", response_model=dict)
async def monitor_all(service: MonitoringService = Depends(get_monitoring_service)):
    """Manually trigger monitoring for all domains"""
    try:
        result = await service.monitor_all_domains()
        return result
    except Exception as e:
        logger.error(f"Error in monitor_all: {e}")
        return {"error": str(e)}


@router.get("/stats", response_model=MonitoringStats)
async def get_stats(repo: MongoRepository = Depends(get_repository)):
    """Get monitoring statistics"""
    try:
        stats = await repo.get_stats()
        return MonitoringStats(
            total_domains=stats.get("total_domains", 0),
            total_subdomains=stats.get("total_subdomains", 0),
            last_check=stats.get("last_updated"),
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return MonitoringStats(total_domains=0, total_subdomains=0)
