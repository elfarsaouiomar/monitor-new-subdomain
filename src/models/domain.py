import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DomainBase(BaseModel):
    """Base domain model"""

    domain: str = Field(..., description="Domain name to monitor")

    @field_validator("domain")
    def validate_domain(cls, v):
        """Validate domain format"""
        v = v.lower().strip()
        # Basic domain validation
        domain_pattern = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
        if not re.match(domain_pattern, v):
            raise ValueError("Invalid domain format")
        return v


class DomainCreate(DomainBase):
    """Request model for creating a domain"""

    notify_slack: bool = False
    notify_telegram: bool = False


class DomainInDB(DomainBase):
    """Domain model as stored in database"""

    subdomains: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notify_slack: bool = False
    notify_telegram: bool = False


class DomainResponse(BaseModel):
    """Response model for domain"""

    id: str
    domain: str
    subdomain_count: int
    created_at: datetime
    updated_at: datetime
    notify_slack: bool
    notify_telegram: bool


class SubdomainResponse(BaseModel):
    """Response model for subdomains"""

    domain: str
    subdomains: List[str]
    total: int


class DomainListResponse(BaseModel):
    """Response model for domain list"""

    domains: List[str]
    total: int


class DNSRecord(BaseModel):
    """DNS record information"""

    subdomain: str
    A: Optional[List[str]] = None
    CNAME: Optional[List[str]] = None


class MonitoringStats(BaseModel):
    """Monitoring statistics"""

    total_domains: int
    total_subdomains: int
    last_check: Optional[datetime] = None
    new_subdomains_found: int = 0
