import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Set

import dns.resolver

from src.core.config import settings
from src.db.repository import repository
from src.models.domain import DNSRecord
from src.services.crtsh_service import Crtsh
from src.services.certspotter_service import CertSpotter
from src.services.notifications_service import Notifications
from src.services.threatminer_service import Threatminer

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for subdomain monitoring operations"""

    def __init__(self):
        self.crtsh = Crtsh()
        self.certspotter = CertSpotter()
        self.threatminer = Threatminer()
        self.notifications = Notifications()

    async def discover_subdomains(self, domain: str) -> Set[str]:
        """Discover subdomains from multiple sources"""
        logger.info(f"Discovering subdomains for {domain}")

        # Run discovery in parallel
        loop = asyncio.get_event_loop()
        crtsh_task = loop.run_in_executor(None, self.crtsh.get_subdomains, domain)
        certspotter_task = loop.run_in_executor(None, self.certspotter.get_subdomains, domain)
        # threatminer_task = loop.run_in_executor(None, self.threatminer.get_subdomains, domain)

        try:
            crtsh_results = await crtsh_task
            certspotter_results = await certspotter_task
            # threatminer_results = await threatminer_task

            # Combine and deduplicate
            all_subdomains = set(crtsh_results + certspotter_results)
            logger.info(f"Found {len(all_subdomains)} subdomains for {domain}")
            return all_subdomains

        except Exception as e:
            logger.error(f"Error discovering subdomains for {domain}: {e}")
            return set()

    async def resolve_dns(self, subdomain: str) -> Optional[DNSRecord]:
        """Resolve DNS records for subdomain"""
        dns_resolver = dns.resolver.Resolver()
        dns_resolver.nameservers = settings.DNS_RESOLVERS
        dns_resolver.timeout = settings.DNS_TIMEOUT
        dns_resolver.lifetime = settings.DNS_TIMEOUT

        dns_record = DNSRecord(subdomain=subdomain)

        try:
            # Resolve A records
            try:
                answers = dns_resolver.resolve(subdomain, "A")
                dns_record.A = [str(rdata) for rdata in answers]
            except (
                dns.resolver.NXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
            ):
                pass

            # Resolve CNAME records
            try:
                answers = dns_resolver.resolve(subdomain, "CNAME")
                dns_record.CNAME = [str(rdata) for rdata in answers]
            except (
                dns.resolver.NXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
            ):
                pass

            # Return only if we found something
            if dns_record.A or dns_record.CNAME:
                return dns_record

        except Exception as e:
            logger.debug(f"DNS resolution failed for {subdomain}: {e}")

        return None

    async def notify_new_subdomains(
        self,
        domain: str,
        new_subdomains: List[str],
        notify_slack: bool,
        notify_telegram: bool,
    ):
        """Send notifications for new subdomains"""
        if not new_subdomains:
            return

        # Resolve DNS for new subdomains
        tasks = [self.resolve_dns(sub) for sub in new_subdomains[:10]]  # Limit to 10
        dns_records = await asyncio.gather(*tasks)

        # Filter out None results
        valid_records = [record for record in dns_records if record]

        if valid_records:
            loop = asyncio.get_event_loop()

            if notify_slack and settings.SLACK_WEBHOOK:
                await loop.run_in_executor(
                    None,
                    self.notifications.slack,
                    self._format_notification(domain, valid_records),
                )

            if notify_telegram and settings.TELEGRAM_BOT_TOKEN:
                await loop.run_in_executor(
                    None,
                    self.notifications.telegram,
                    self._format_notification(domain, valid_records),
                )

    def _format_notification(self, domain: str, dns_records: List[DNSRecord]) -> str:
        """Format notification message"""
        message = f"🔍 New subdomains found for {domain}\n\n"
        for record in dns_records:
            message += f"• {record.subdomain}\n"
            if record.A:
                message += f"  A: {', '.join(record.A)}\n"
            if record.CNAME:
                message += f"  CNAME: {', '.join(record.CNAME)}\n"
        return message

    async def add_domain(
        self, domain: str, notify_slack: bool = False, notify_telegram: bool = False
    ) -> dict:
        """Add domain and discover initial subdomains"""
        # Check if exists
        exists = await repository.exists(domain)
        if exists:
            raise Exception("Domain already exists")

        # Discover subdomains
        subdomains = await self.discover_subdomains(domain)

        # Add to database
        domain_data = {
            "domain": domain,
            "subdomains": list(subdomains),
            "notify_slack": notify_slack,
            "notify_telegram": notify_telegram,
        }

        result = await repository.add_domain(domain_data)
        logger.info(f"Added domain {domain} with {len(subdomains)} subdomains")

        return result

    async def monitor_domain(self, domain: str) -> int:
        """Monitor single domain for new subdomains"""
        logger.info(f"Monitoring {domain}")

        # Get existing domain
        existing = await repository.find_one(domain)
        if not existing:
            logger.warning(f"Domain {domain} not found")
            return 0

        # Discover current subdomains
        current_subdomains = await self.discover_subdomains(domain)

        # Find new subdomains
        old_subdomains = set(existing.get("subdomains", []))
        new_subdomains = list(current_subdomains - old_subdomains)

        if new_subdomains:
            # Update database
            await repository.update_subdomains(domain, new_subdomains)
            logger.info(f"Found {len(new_subdomains)} new subdomains for {domain}")

            # Send notifications
            await self.notify_new_subdomains(
                domain,
                new_subdomains,
                existing.get("notify_slack", False),
                existing.get("notify_telegram", False),
            )

        return len(new_subdomains)

    async def monitor_all_domains(self) -> dict:
        """Monitor all domains in database"""
        logger.info("Starting monitoring for all domains")

        domains = await repository.get_all_domains_list()
        logger.info(f"Monitoring {len(domains)} domains")

        # Monitor domains concurrently with limit
        semaphore = asyncio.Semaphore(settings.MAX_WORKERS)

        async def monitor_with_semaphore(domain):
            async with semaphore:
                return await self.monitor_domain(domain)

        tasks = [monitor_with_semaphore(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        total_new = sum(r for r in results if isinstance(r, int))
        errors = sum(1 for r in results if isinstance(r, Exception))

        logger.info(f"Monitoring complete: {total_new} new subdomains, {errors} errors")

        return {
            "domains_monitored": len(domains),
            "new_subdomains_found": total_new,
            "errors": errors,
            "timestamp": datetime.utcnow(),
        }


# Global service instance
monitoring_service = MonitoringService()
