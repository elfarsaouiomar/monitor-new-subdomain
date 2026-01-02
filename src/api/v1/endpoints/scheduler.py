import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from src.core.config import settings
from src.scheduler.scheduler import monitoring_scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    if not settings.ENABLE_SCHEDULER:
        return {"enabled": False, "message": "Scheduler is disabled in configuration"}

    return {
        "enabled": True,
        "running": monitoring_scheduler.is_running,
        "interval_minutes": settings.MONITOR_INTERVAL_MINUTES,
        "timezone": settings.SCHEDULER_TIMEZONE,
        "next_run": monitoring_scheduler.get_next_run_time(),
        "current_time": datetime.utcnow(),
    }


@router.get("/jobs")
async def list_jobs() -> List[Dict[str, Any]]:
    """List all scheduled jobs"""
    if not settings.ENABLE_SCHEDULER or not monitoring_scheduler.is_running:
        raise HTTPException(status_code=400, detail="Scheduler is not running")

    jobs = monitoring_scheduler.get_jobs()

    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger),
        }
        for job in jobs
    ]


@router.post("/trigger")
async def trigger_monitoring() -> Dict[str, Any]:
    """Manually trigger monitoring job immediately"""
    if not settings.ENABLE_SCHEDULER or not monitoring_scheduler.is_running:
        raise HTTPException(
            status_code=400,
            detail="Scheduler is not running. Use /api/v1/monitoring/check-all instead",
        )

    success = monitoring_scheduler.trigger_now()

    if success:
        return {
            "message": "Monitoring job triggered successfully",
            "next_run": monitoring_scheduler.get_next_run_time(),
        }

    raise HTTPException(status_code=500, detail="Failed to trigger monitoring job")


@router.post("/pause")
async def pause_scheduler() -> Dict[str, str]:
    """Pause the scheduler"""
    if not settings.ENABLE_SCHEDULER or not monitoring_scheduler.is_running:
        raise HTTPException(status_code=400, detail="Scheduler is not running")

    monitoring_scheduler.pause()
    return {"message": "Scheduler paused"}


@router.post("/resume")
async def resume_scheduler() -> Dict[str, str]:
    """Resume the scheduler"""
    if not settings.ENABLE_SCHEDULER:
        raise HTTPException(
            status_code=400, detail="Scheduler is disabled in configuration"
        )

    monitoring_scheduler.resume()
    return {
        "message": "Scheduler resumed",
        "next_run": str(monitoring_scheduler.get_next_run_time()),
    }
