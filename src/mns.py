#!/usr/bin/env python
# I don't believe in the license, you can do whatever you like

import argparse, threading, dns.resolver, requests.packages.urllib3

from termcolor import colored
from multiprocessing import Process, Queue

from src.config.Config import RESOLVERS_LIST
from src.service.Crtsh import Crtsh
from src.db.MnsRepository import MnsRepository
from src.service.functions import get_current_time, notification_template, custom_logger
from src.service.Notifications import Notifications
from src.service.Threatminer import Threatminer

# disable requests warnings
requests.packages.urllib3.disable_warnings()

# Create and configure logger
logger = custom_logger("Sub_Domain_Monitoring")


class SubDomainMonitoring:
	db_client = db()
	send_notification = notifications()
	crtsh = Crtsh()
	threatminer = Threatminer()
	slack = telegram = False
	
	def get_new_subdomains(self, domain) -> dict:
		"""
		Todo: add comments
		"""
		print('ddddddd')
		subdomains = dict()
		subdomains['domain'] = domain
		subdomains["subdomains"] = list(set(
				self.crtsh.get_subdomains(domain=domain) +
				self.threatminer.get_subdomains(domain=domain))
		)
		return subdomains
	
	def resolver_new_subdomains(self, subdomain) -> None:
		dns_resolver = dns.resolver.Resolver()
		dns_resolver.nameservers = RESOLVERS_LIST
		
		dns_results = dict()
		dns_results['subdomain'] = subdomain
		print(subdomain)
		try:
			for qtype in ['A', 'CNAME']:
				
				answers = dns_resolver.resolve(subdomain, qtype)
				
				if answers.rrset is None:
					pass
				
				elif answers.rdtype == 1:
					a_records = [str(i) for i in answers.rrset]
					dns_results["A"] = a_records
				
				elif answers.rdtype == 5:
					cname_records = [str(i) for i in answers.rrset]
					dns_results["CNAME"] = cname_records
		
		except dns.exception.DNSException:
			
			pass
		
		except Exception as e:
			logger.error(f"[!] Error while resolving subdomains {e}")
		
		finally:
			if dns_results.get('A') is not None and dns_results.get('CNAME') is not None:
				self.notify(message=dns_results)
	
	def notify(self, message) -> None:
		""" send message via slack Or Telegram """
		
		self.send_notification.slack(notification_template(message)) if self.slack else None
		
		self.send_notification.telegrame(notification_template(message)) if self.telegram else None
	
	def compaire(self, subdomains) -> None:
		""" Compare a list of given subdomains and :return: return a new subdomains list """
		
		domain = subdomains.get('domain')
		new_subdomains = subdomains.get('subdomains')
		
		# get all subdomains by domain name from dbs
		target = self.db_client.find_one(domain=domain)
		
		if target is None:
			logger.info(f"[+] new target {domain} : {len(new_subdomains)} subdomain ")
			self.db_client.add_domain(target=subdomains)
		else:
			if len(new_subdomains) > 0:
				old_subdomains = target.get('subdomains')
				diff = [x for x in new_subdomains if x not in old_subdomains]
				if len(diff) > 0:
					self.db_client.update_domain(domain, diff)
					logger.info(f"[+] {len(diff)} new subdomains found for {domain}")
					for subdomain in diff:
						pthread = threading.Thread(
								target=self.resolver_new_subdomains, args=(subdomain,))
						pthread.start()
	
	def add(self, domain) -> None:
		""" Add new domain to Monitoring """
		
		if self.db_client.find_one(domain=domain) is None:
			self.compaire(self.get_new_subdomains(domain=domain))
		else:
			logger.info(f"[+] {domain} already exist in database")
	
	async def read_file(self, file) -> object:
		return open(file, 'r').readlines()
	
	def import_domains_from_file(self, file) -> None:
		""" import list of domains from a text file """
		
		domains = self.read_file(file)
		
		procs = []
		
		for i in domains:
			domain = i.strip()
			if domain:
				proc = Process(target=self.add, args=(domain,))
				procs.append(proc)
				logger.info(f"[+] add new target {domain}")
		
		for p in procs:
			p.start()
		
		for wait_for_proc in procs:
			wait_for_proc.join()
	
	def list_all_domains(self) -> list:
		""" list all domains from the DB """
		
		for results in self.db_client.find_all():
			print(colored(f"[+] {results.get('domain')} {len(results.get('subdomains'))}", "green"))
	
	def get_subdomains(self, domain) -> object:
		""" return a list of subdomain for given domain """
		
		target = self.db_client.find_one(domain=domain)
		if target is not None:
			target = target.get('subdomains')
			for i in target:
				print(colored(f"{i}", "green"))
		else:
			logger.info(f"{domain} not exist in database")
	
	async def delete_domain(self, domain) -> None:
		""" Delete domain from database """
		
		target = self.db_client.find_one(domain=domain)
		if target is not None:
			self.db_client.delete_domain(domain=domain)
			logger.info(f"Delete {domain} from database")
		else:
			logger.info(f"{domain} not exist in database")
	
	def export(self) -> None:
		""" export all subdomain to text file """
		
		total = 0
		all_domains = self.db_client.find_all()
		
		with open("export-" + get_current_time() + ".txt", "w") as file:
			for domain in all_domains:
				total = total + len(domain.get('subdomains'))
				for subdomain in domain.get('subdomains'):
					file.write(subdomain + "\n")
		file.close()
		logger.info(f"[+] Export {total} from database")
	
	def worker(self, proccess):
		p = Process(target=self.compaire, args=(1,))
		p.start()
	
	def monitor(self) -> None:
		""" Monitor All domains in database """
		
		processes = []
		# print(self.get_new_subdomains(target.get('domain')))
		
		domains = [target.get('domain') for target in self.db_client.find_all()]
		queue = Queue()
		
		queue.put(Process(target=self.compaire, args=(
			self.get_new_subdomains(
					domains
			),)).start())
		
		print("HOP")
		print(processes)
		
		for proc in processes:
			proc.start()
	
	def init_args(self):
		parser = argparse.ArgumentParser(
				description='Simple tools to monitoring new subdomains')
		
		parser.add_argument("-m", "--monitor", help="looking for new subdomain",
		                    type=bool,
		                    metavar='',
		                    required=False,
		                    nargs='?',
		                    const=True)
		
		parser.add_argument("-a", "--add",
		                    help="Domain to monitor. E.g: domain.com",
		                    type=str,
		                    metavar='',
		                    required=False)
		
		parser.add_argument("-l", "--listdomains",
		                    help="list all domain on database",
		                    type=bool,
		                    metavar='',
		                    required=False,
		                    const=True,
		                    nargs='?')
		
		parser.add_argument("-i", "--importfile",
		                    help="import Domains From File",
		                    type=str,
		                    metavar='',
		                    required=False)
		
		parser.add_argument("-L", "--listsubdomains",
		                    help="list all domain on for domain",
		                    type=str,
		                    metavar='',
		                    required=False)
		
		parser.add_argument("-d", "--delete",
		                    help="disable for monitoring",
		                    type=str,
		                    metavar='',
		                    required=False)
		
		parser.add_argument("-e", "--export",
		                    help="export all subdomains for all domains into single file",
		                    type=bool,
		                    metavar='',
		                    required=False,
		                    const=True,
		                    nargs='?')
		
		parser.add_argument("-s", "--slack",
		                    help="send notification via slack",
		                    type=bool, metavar='',
		                    required=False,
		                    const=True, nargs='?')
		
		parser.add_argument("-t", "--telegram",
		                    help="send notification via telegram",
		                    type=bool,
		                    metavar='',
		                    required=False,
		                    const=True,
		                    nargs='?')
		
		return parser.parse_args()
	
	def main(self, args):
		
		if args.slack:
			self.slack = True
		
		if args.telegram:
			self.telegram = True
		
		if args.listdomains:
			self.list_all_domains()
		
		elif args.listsubdomains:
			self.get_subdomains(domain=args.listsubdomains)
		
		elif args.delete:
			self.delete_domain(domain=args.delete)
		
		elif args.add:
			self.add(domain=args.add)
		
		elif args.importfile:
			self.import_domains_from_file(file=args.importfile)
		
		elif args.export:
			self.export()
		
		elif args.monitor:
			await self.monitor()
		
		else:
			await self.monitor()
