import logging
from datetime import datetime

from src.db.repository import repository
from src.services.monitoring_service import monitoring_service

logger = logging.getLogger(__name__)


async def scheduled_monitoring_job():
    """
    Background job that runs monitoring for all domains
    This is executed by APScheduler at configured intervals
    """
    logger.info("=" * 60)
    logger.info(f"Starting scheduled monitoring job at {datetime.utcnow()}")
    logger.info("=" * 60)

    try:
        # Ensure we're connected
        if not repository.client:
            await repository.connect()

        # Run monitoring for all domains
        result = await monitoring_service.monitor_all_domains()

        logger.info("Scheduled monitoring completed:")
        logger.info(f"  - Domains monitored: {result['domains_monitored']}")
        logger.info(f"  - New subdomains found: {result['new_subdomains_found']}")
        logger.info(f"  - Errors: {result['errors']}")
        logger.info("=" * 60)

        return result

    except Exception as e:
        logger.error(f"Scheduled monitoring job failed: {e}", exc_info=True)
        return {"error": str(e)}
