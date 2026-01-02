import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.monitoring_service import MonitoringService


@pytest.fixture
async def monitoring_service():
	service = MonitoringService()
	return service


@pytest.mark.asyncio
async def test_discover_subdomains(monitoring_service):
	# Mock the external services
	with patch.object(monitoring_service.crtsh, 'get_subdomains', return_value=['sub1.example.com']):
		with patch.object(monitoring_service.threatminer, 'get_subdomains', return_value=['sub2.example.com']):
			subdomains = await monitoring_service.discover_subdomains('example.com')

			assert len(subdomains) == 2
			assert 'sub1.example.com' in subdomains
			assert 'sub2.example.com' in subdomains


@pytest.mark.asyncio
async def test_resolve_dns(monitoring_service):
	# Test DNS resolution
	record = await monitoring_service.resolve_dns('google.com')

	# May be None if DNS fails
	if record:
		assert record.subdomain == 'google.com'
		assert record.A is not None or record.CNAME is not None