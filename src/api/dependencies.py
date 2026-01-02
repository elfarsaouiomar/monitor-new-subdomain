from src.db.repository import repository
from src.services.monitoring_service import monitoring_service


async def get_repository():
    """Dependency for repository"""
    return repository


async def get_monitoring_service():
    """Dependency for monitoring service"""
    return monitoring_service
