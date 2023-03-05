#!/usr/bin/env python
# I don't believe in the license, you can do whatever you like

from src.notifications import notifications
from src.functions import get_current_time, notification_template, custom_logger
from src.config import RESOLVERS_LIST
from src.db import db
from termcolor import colored
from requests import get, exceptions
from logging import basicConfig, getLogger, DEBUG, info, error, critical, StreamHandler, debug, warning 
import requests.packages.urllib3
import dns.resolver
from json import loads
import threading
import argparse
from random import choice



# disable requests warnings
requests.packages.urllib3.disable_warnings()
 
# Create and configure logger
logger = custom_logger("Sub_Domain_Monitoring")

class SubDomainMonitoring:

    db_client = db()
    send_notification = notifications()
    slack = telegram = False

    def parse_crt_response(self, subdomains):
        """ parse crt and return list of subomians (sort, clean, uniq) """
        new_subdomains = list()
        try:
            for i in subdomains:
                listsubdomians = i.split('\n')
                for subDomain in listsubdomians:
                    if subDomain not in new_subdomains:
                        subDomain = subDomain.replace("*.", "").replace("@", ".")
                        new_subdomains.append(subDomain)

        except Exception as e:
            print(
                colored("[!] error on parsing crt response \n [!] {}".format(e), "red"))

        return new_subdomains

    def get_subdomains_from_Threatminer(self, domain):
        """ get list from Threatminer """

        url = f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=5"
        
        res = get(url=url, timeout=30)

        res.raise_for_status()
        
        resp = res.json()
        if resp.get('results') is not None:
            return resp.get('results')
        return []

    def get_new_subdomains(self, domain):
        resultSubdomains = dict()
        resultSubdomains['domain'] = domain
        resultSubdomains["subdomains"] = list(set(
            self.get_subdomains_from_crt(domain=domain) +
            self.get_subdomains_from_Threatminer(domain=domain))
        )

        return resultSubdomains

    def get_subdomains_from_crt(self, domain):
        """ get list of subdomain from crt """
        resultSubdomains = []
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0"
            }

            req = get(url, headers=headers, timeout=30, verify=False)

            req.raise_for_status()

            content = req.content.decode('utf-8')
            data = loads(content)

            subdomains = set()
            for subdomain in data:
                subdomains.add(subdomain["name_value"].lower())
            resultSubdomains = self.parse_crt_response(sorted(subdomains))

            return resultSubdomains

        except Exception as e:
            print(
                colored("[!] error while requesting {} \n[!] {}".format(domain, e), "red"))

        return resultSubdomains

    def resolver_new_subdomains(self, subdomain):
        dns_resolver = dns.resolver.Resolver()
        dns_resolver.nameservers = resolverList

        dnsResult = dict()
        dnsResult['subdomain'] = subdomain
        try:
            for qtype in ['A', 'CNAME']:

                answers = dns_resolver.resolve(subdomain, qtype)

                if answers.rrset is None:
                    pass

                elif answers.rdtype == 1:
                    a_records = [str(i) for i in answers.rrset]
                    dnsResult["A"] = a_records

                elif answers.rdtype == 5:
                    cname_records = [str(i) for i in answers.rrset]
                    dnsResult["CNAME"] = cname_records

        except dns.exception.DNSException:
            pass

        except Exception as e:
            print(
                colored("[!] Error while resolving subdomain \n[!] {}".format(e), "red"))

        finally:
            if dnsResult.get('A') is not None and dnsResult.get('CNAME') is not None:
                self.notify(message=dnsResult)

    def notify(self, message):
        """ send message via slack Or Telegram """

        self.send_notification.slack(notification_template(message)) if self.slack else None
            
        self.send_notification.telegrame(notification_template(message)) if self.telegram else None

    def compaire(self, subdomians):
        """ Compate a list of given subdomains and :return: return new subdomains """

        try:
            domain = subdomians.get('domain')
            newsubDomain = subdomians.get('subdomains')
            # get all subdomian by domian name
            target = self.db_client.find_one(domain=domain)

            if target is None:
                print(colored("[+] new target {domain} : {length} subdomain ".format(
                    domain=domain, length=len(newsubDomain)), "green"))
                self.db_client.add_domain(target=subdomians)
            else:
                if len(newsubDomain) > 0:
                    oldSubdomain = target.get('subdomains')
                    diff = [x for x in newsubDomain if x not in oldSubdomain]
                    if len(diff) > 0:
                        self.db_client.update_domain(domain, diff)
                        print(colored(
                            "[+] {0} new subdomains found for {1}".format(len(diff), domain), "green"))
                        for subdomian in diff:
                            pthread = threading.Thread(
                                target=self.resolver_new_subdomains, args=(subdomian,))
                            pthread.start()

        except Exception as e:
            print(
                colored("[!] error while comparing result \n[!] {}".format(e), "red"))

    def add(self, domain):
        """ Add new domain to Monitoring """
        
        if self.db_client.find_one(domain=domain) is None:
            self.compaire(self.get_new_subdomains(domain=domain))
        else:
            print(
                colored("[+] {} already exist in database".format(domain), "green"))

    def readfile(self, file):
        return open(file, 'r').readlines()

    def import_domains_from_file(self, file):
        """ import list of domains from a text file """
        try:
            domains = self.readfile(file)
            for i in domains:
                domain = i.strip()
                if domain:
                    print(colored("[+] import : ", "blue") +
                          colored(domain, 'green', attrs=['reverse']))
                    t = threading.Thread(target=self.add, args=(domain,))
                    t.start()

        except Exception as e:
            print(colored("[!] {0}".format(e), "red"))

    def list_all_domains(self):
        """ list all domains  monitoring in DB """
        for domain in self.db_client.find_all():
            print(colored("[+] {}".format(domain.get('domain')), "green"),
                  colored("{0}".format(len(domain.get('subdomains'))), "green"))

    def get_subdomains(self, domain):
        """ return a list of subdomain for given domain """

        target = self.db_client.find_one(domain=domain)
        if target is not None:
            target = target.get('subdomains')
            for i in target:
                print(i)
        else:
            logger.info(f"{domain} not exist in database")


    def delete_domain(self, domain):
        """ Delete domain from database """

        self.db_client.delete_domain(domain=domain)
        logger.info(f"Delete {domain} from database")

    def export(self):
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



    def monitor(self):
        """ Monitor All domains in database """

        for domain in self.db_client.find_all():
            print(colored("[+] Checking : ", "blue") +colored(domain.get('domain'), 'green', attrs=['reverse']))
            logger.info(f"Checking")
            thread = threading.Thread(target=self.compaire, args=(
                self.get_new_subdomains(domain.get('domain')),))
            thread.start()

    def initArgparse(self):
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
            self.monitor()


def banner():
    colors = ['red', 'green', 'blue', 'yellow', 'magenta']
    version = "2.0"
    BANNER = f"""

        ███╗   ███╗███╗   ██╗███████╗
        ████╗ ████║████╗  ██║██╔════╝
        ██╔████╔██║██╔██╗ ██║███████╗
        ██║╚██╔╝██║██║╚██╗██║╚════██║
        ██║ ╚═╝ ██║██║ ╚████║███████║
        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝
        ## Monitor New Subdomains
        ## @omarelfarsaoui
        ## version {version}
    """
    print(colored(BANNER, choice(colors)))


if __name__ == "__main__":
    try:
        banner()
        subdomainMonitoring = SubDomainMonitoring()
        args = subdomainMonitoring.initArgparse()
        subdomainMonitoring.main(args)


    except exceptions.HTTPError as errh:
        print (colored(f"[-] Http Error: {errh}", "red"))
        
    except exceptions.ConnectionError as errc:
        print (colored(f"[-] Error Connecting: {errc}", "red"))
        
    except exceptions.Timeout as errt:
        print (colored(f"[-] Timeout Error: {errt}", "red"))

    except exceptions.RequestException as err:
        print (colored(f"[-] OOps: Something Else {err}", "red"))

    except KeyboardInterrupt:
        logger.info("[-] Ctrl+c detected")
        exit(0)

    except Exception as err:
        logger.error(err)
        exit(1)

