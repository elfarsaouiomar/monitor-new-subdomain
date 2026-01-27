import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import settings
from src.scheduler.jobs import scheduled_monitoring_job

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """APScheduler wrapper for monitoring jobs"""

    def __init__(self):
        self.scheduler = None
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if not settings.ENABLE_SCHEDULER:
            logger.info("Scheduler is disabled in configuration")
            return

        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Initializing APScheduler...")

        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)

        # Add the monitoring job
        self.scheduler.add_job(
            scheduled_monitoring_job,
            trigger=IntervalTrigger(minutes=settings.MONITOR_INTERVAL_MINUTES),
            id="monitoring_job",
            name="Subdomain Monitoring",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
            coalesce=True,  # Combine missed runs
            misfire_grace_time=300,  # 5 minutes grace period
        )

        # Start the scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info(f"Scheduler started successfully")
        logger.info(
            f"  - Monitoring interval: {settings.MONITOR_INTERVAL_MINUTES} minutes"
        )
        logger.info(f"  - Timezone: {settings.SCHEDULER_TIMEZONE}")
        logger.info(f"  - Next run: {self.get_next_run_time()}")

    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler"""
        if self.scheduler and self.is_running:
            logger.info("Shutting down scheduler...")
            self.scheduler.shutdown(wait=wait)
            self.is_running = False
            logger.info("Scheduler shutdown complete")

    def pause(self):
        """Pause the scheduler"""
        if self.scheduler and self.is_running:
            self.scheduler.pause()
            logger.info("Scheduler paused")

    def resume(self):
        """Resume the scheduler"""
        if self.scheduler:
            self.scheduler.resume()
            logger.info("Scheduler resumed")

    def get_next_run_time(self):
        """Get next scheduled run time"""
        if self.scheduler and self.is_running:
            job = self.scheduler.get_job("monitoring_job")
            if job:
                return job.next_run_time
        return None

    def get_jobs(self):
        """Get all scheduled jobs"""
        if self.scheduler:
            return self.scheduler.get_jobs()
        return []

    def trigger_now(self):
        """Manually trigger the monitoring job now"""
        if self.scheduler and self.is_running:
            logger.info("Manually triggering monitoring job...")
            self.scheduler.modify_job("monitoring_job", next_run_time=datetime.now())
            return True
        return False


# Global scheduler instance
monitoring_scheduler = MonitoringScheduler()
