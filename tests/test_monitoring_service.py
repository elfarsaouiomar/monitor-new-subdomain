import pytest
from unittest.mock import patch
from src.services.monitoring_service import MonitoringService


@pytest.fixture
def monitoring_service():
    return MonitoringService()


# @pytest.mark.asyncio
# async def test_discover_subdomains(monitoring_service):
#     with patch.object(
#         monitoring_service.crtsh,
#         "get_subdomains",
#         return_value=["google.com"],
#     ), patch.object(
#         monitoring_service.threatminer,
#         "get_subdomains",
#         return_value=["drive.google.com"],
#     ):
#         subdomains = await monitoring_service.discover_subdomains("google.com")

#     assert set(subdomains) == {
#         "plus.google.com",
#         "drive.google.com",
#     }


@pytest.mark.asyncio
async def test_resolve_dns(monitoring_service):
    record = await monitoring_service.resolve_dns("google.com")

    if record is None:
        pytest.skip("DNS resolution unavailable")

    assert record.subdomain == "google.com"
    assert record.A or record.CNAME
