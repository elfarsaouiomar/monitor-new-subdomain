import argparse
import asyncio
import sys
from pathlib import Path
from termcolor import colored
from src.core.config import settings
from src.db.repository import repository
from src.services.monitoring_service import monitoring_service
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SubDomainMonitorCLI:
    """Command-line interface for subdomain monitoring"""

    def __init__(self):
        self.repo = repository
        self.service = monitoring_service

    async def add_domain(
        self, domain: str, slack: bool = False, telegram: bool = False
    ):
        """Add new domain to monitoring"""
        try:
            await self.repo.connect()
            result = await self.service.add_domain(domain, slack, telegram)
            subdomain_count = len(result.get("subdomains", []))
            logger.info(
                colored(f"Added {domain} with {subdomain_count} subdomains", "green")
            )
        except Exception as e:
            logger.error(colored(f"Failed to add domain: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def import_from_file(
        self, file_path: str, slack: bool = False, telegram: bool = False
    ):
        """Import domains from file"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(colored(f"File not found: {file_path}", "red"))
                return

            await self.repo.connect()

            with open(file_path, "r") as f:
                domains = [line.strip() for line in f if line.strip()]

            logger.info(f"Importing {len(domains)} domains...")

            for domain in domains:
                try:
                    await self.service.add_domain(domain, slack, telegram)
                    logger.info(colored(f"Added {domain}", "green"))
                except Exception as e:
                    logger.error(colored(f"Failed to add {domain}: {e}", "red"))

        except Exception as e:
            logger.error(colored(f"Import failed: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def list_domains(self):
        """List all monitored domains"""
        try:
            await self.repo.connect()
            domains = await self.repo.find_all()

            if not domains:
                print(colored("No domains found", "yellow"))
                return

            print(
                colored(f"\n{'Domain':<40} {'Subdomains':<15} {'Last Updated'}", "cyan")
            )
            print(colored("-" * 80, "cyan"))

            for domain in domains:
                name = domain.get("domain", "N/A")
                count = len(domain.get("subdomains", []))
                updated = domain.get("updated_at", "N/A")
                print(colored(f"{name:<40} {count:<15} {updated}", "green"))

            print(colored(f"\nTotal: {len(domains)} domains", "cyan"))

        except Exception as e:
            logger.error(colored(f"Failed to list domains: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def list_subdomains(self, domain: str):
        """List subdomains for a specific domain"""
        try:
            await self.repo.connect()
            doc = await self.repo.find_one(domain)

            if not doc:
                logger.error(colored(f"Domain {domain} not found", "red"))
                return

            subdomains = doc.get("subdomains", [])

            if not subdomains:
                print(colored(f"No subdomains found for {domain}", "yellow"))
                return

            print(colored(f"\nSubdomains for {domain}:", "cyan"))
            print(colored("-" * 80, "cyan"))

            for subdomain in sorted(subdomains):
                print(colored(f"{subdomain}", "green"))

            print(colored(f"\nTotal: {len(subdomains)} subdomains", "cyan"))

        except Exception as e:
            logger.error(colored(f"Failed to list subdomains: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def delete_domain(self, domain: str):
        """Delete domain from monitoring"""
        try:
            await self.repo.connect()
            deleted = await self.repo.delete_domain(domain)

            if deleted:
                logger.info(colored(f"Deleted {domain}", "green"))
            else:
                logger.error(colored(f"Domain {domain} not found", "red"))

        except Exception as e:
            logger.error(colored(f"Failed to delete domain: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def export_subdomains(self):
        """Export all subdomains to a file"""
        try:
            await self.repo.connect()
            domains = await self.repo.find_all()

            from datetime import datetime

            filename = (
                f"subdomains_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

            total_subdomains = 0
            with open(filename, "w") as f:
                for domain in domains:
                    subdomains = domain.get("subdomains", [])
                    for subdomain in subdomains:
                        f.write(f"{subdomain}\n")
                        total_subdomains += 1

            logger.info(
                colored(
                    f"Exported {total_subdomains} subdomains to {filename}", "green"
                )
            )

        except Exception as e:
            logger.error(colored(f"Export failed: {e}", "red"))
        finally:
            await self.repo.disconnect()

    async def monitor(self):
        """Run monitoring for all domains"""
        try:
            await self.repo.connect()
            logger.info(colored("Starting monitoring...", "cyan"))

            result = await self.service.monitor_all_domains()

            print(colored("\n" + "=" * 50, "cyan"))
            print(colored("Monitoring Results:", "cyan"))
            print(colored("=" * 50, "cyan"))
            print(colored(f"Domains monitored: {result['domains_monitored']}", "green"))
            print(
                colored(
                    f"New subdomains found: {result['new_subdomains_found']}", "green"
                )
            )
            print(
                colored(
                    f"Errors: {result['errors']}",
                    "yellow" if result["errors"] > 0 else "green",
                )
            )
            print(colored("=" * 50, "cyan"))

        except Exception as e:
            logger.error(colored(f"Monitoring failed: {e}", "red"))
        finally:
            await self.repo.disconnect()

    def init_args(self):
        """Initialize argument parser"""
        parser = argparse.ArgumentParser(
            description="Professional subdomain monitoring tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "-a",
            "--add",
            type=str,
            metavar="DOMAIN",
            help="Add domain to monitor (e.g., example.com)",
        )

        parser.add_argument(
            "-i",
            "--import-file",
            type=str,
            metavar="FILE",
            help="Import domains from file (one per line)",
        )

        parser.add_argument(
            "-l",
            "--list-domains",
            action="store_true",
            help="List all monitored domains",
        )

        parser.add_argument(
            "-L",
            "--list-subdomains",
            type=str,
            metavar="DOMAIN",
            help="List subdomains for specific domain",
        )

        parser.add_argument(
            "-d",
            "--delete",
            type=str,
            metavar="DOMAIN",
            help="Delete domain from monitoring",
        )

        parser.add_argument(
            "-e", "--export", action="store_true", help="Export all subdomains to file"
        )

        parser.add_argument(
            "-m",
            "--monitor",
            action="store_true",
            help="Run monitoring for all domains",
        )

        parser.add_argument(
            "-s", "--slack", action="store_true", help="Send notifications via Slack"
        )

        parser.add_argument(
            "-t",
            "--telegram",
            action="store_true",
            help="Send notifications via Telegram",
        )

        return parser.parse_args()

    async def main(self):
        """Main CLI entry point"""
        args = self.init_args()

        if args.add:
            await self.add_domain(args.add, args.slack, args.telegram)

        elif args.import_file:
            await self.import_from_file(args.import_file, args.slack, args.telegram)

        elif args.list_domains:
            await self.list_domains()

        elif args.list_subdomains:
            await self.list_subdomains(args.list_subdomains)

        elif args.delete:
            await self.delete_domain(args.delete)

        elif args.export:
            await self.export_subdomains()

        elif args.monitor:
            await self.monitor()

        else:
            # Default action: run monitoring
            await self.monitor()


def main():
    """Entry point for CLI"""
    cli = SubDomainMonitorCLI()
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()
