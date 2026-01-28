import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_monitoring_service, get_repository
from src.db.repository import MongoRepository
from src.models.domain import (DomainCreate, DomainListResponse,
                               DomainResponse, SubdomainResponse)
from src.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("", response_model=DomainListResponse)
async def list_domains(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repo: MongoRepository = Depends(get_repository),
):
    """List all monitored domains"""
    try:
        domains = await repo.get_all_domains_list()
        return DomainListResponse(domains=domains, total=len(domains))
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail="Failed to list domains")


@router.get("/{domain}/subdomains", response_model=SubdomainResponse)
async def get_subdomains(domain: str, repo: MongoRepository = Depends(get_repository)):
    """Get all subdomains for a specific domain"""
    try:
        doc = await repo.find_one(domain)
        if not doc:
            raise HTTPException(status_code=404, detail="Domain not found")

        subdomains = doc.get("subdomains", [])
        return SubdomainResponse(
            domain=domain, subdomains=subdomains, total=len(subdomains)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subdomains for {domain}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subdomains")


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain_create: DomainCreate,
    service: MonitoringService = Depends(get_monitoring_service),
):
    """Add a new domain to monitor"""
    try:
        result = await service.add_domain(
            domain_create.domain,
            domain_create.notify_slack,
            domain_create.notify_telegram,
        )
        return {
            "message": "Domain added successfully",
            "domain": domain_create.domain,
            "subdomain_count": len(result.get("subdomains", [])),
        }
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail="Domain already exists")
        logger.error(f"Error adding domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{domain}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(domain: str, repo: MongoRepository = Depends(get_repository)):
    """Delete a domain from monitoring"""
    try:
        deleted = await repo.delete_domain(domain)
        if not deleted:
            raise HTTPException(status_code=404, detail="Domain not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting domain {domain}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete domain")


@router.post("/{domain}/check", response_model=dict)
async def check_domain(
    domain: str,
    service: MonitoringService = Depends(get_monitoring_service),
    repo: MongoRepository = Depends(get_repository),
):
    """Manually trigger monitoring check for specific domain"""
    try:
        exists = await repo.exists(domain)
        if not exists:
            raise HTTPException(status_code=404, detail="Domain not found")

        new_count = await service.monitor_domain(domain)
        return {
            "message": "Monitoring check completed",
            "domain": domain,
            "new_subdomains_found": new_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking domain {domain}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check domain")
