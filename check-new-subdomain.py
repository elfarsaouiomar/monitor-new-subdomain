#!/usr/bin/env python
# I don't believe in the license, you can do whatever you like

version = "1.1"


import argparse
import threading
from json import loads
import dns.resolver
import requests.packages.urllib3
from requests import get
from termcolor import colored

from src.ConfigDB import ConfigDB
from src.Config import resolverList
from src.Functions import getCurrentTime, notificationTemplate
from src.Notifications import Notifications

# disable requests warnings
requests.packages.urllib3.disable_warnings()

class SubDomainMonitoring:
    db = ConfigDB()
    sendNotification = Notifications()
    slack = telegram = saveToFile = False

    def parseCrtResponse(self, subdomains):
        """ parse crt and return list of subomians (sort, clean, uniq) """
        newSubdomains = list()
        try:
            for i in subdomains:
                listsubdomians = i.split('\n')
                for subDomain in listsubdomians:
                    if subDomain not in newSubdomains:
                        subDomain = subDomain.replace("*.", "").replace("@", ".")
                        newSubdomains.append(subDomain)

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] error on parsing crt response \n [!] {}".format(e), "red"))

        return newSubdomains

    def getFromThreatminer(self, domain):
        """ get list from Threatminer """
        url = "https://api.threatminer.org/v2/domain.php?q={}&rt=5".format(domain)
        res = get(url)
        if res.status_code != 200:
            return []
        resp = res.json()
        if resp.get('results') is not None:
            return resp.get('results')
        return []

    def getdomain(self, domain):
        resultSubdomains = dict()
        resultSubdomains['domain'] = domain
        resultSubdomains["subdomains"] = list(set(
            self.getFromCrt(domain=domain) + 
            self.getFromThreatminer(domain=domain))
            )

        return resultSubdomains

    def getFromCrt(self, domain):
        """ get list of subdomain from crt """
        resultSubdomains = list()
        try:
            base_url = "https://crt.sh/?q={}&output=json"
            victim = "%25.{}".format(domain)
            url = base_url.format(victim)

            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'
            req = get(url, headers={'User-Agent': user_agent}, timeout=30, verify=False)

            if req.status_code == 200:
                content = req.content.decode('utf-8')
                data = loads(content)
                subdomains = set()
                for subdomain in data:
                    subdomains.add(subdomain["name_value"].lower())
                resultSubdomains = self.parseCrtResponse(sorted(subdomains))
            return resultSubdomains

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while requesting {} \n[!] {}".format(domain, e), "red"))

        return resultSubdomains

    def scanSubdomain(self, subdomain):
        dnsResolver = dns.resolver.Resolver()
        dnsResolver.nameservers = resolverList

        dnsResult = dict()
        dnsResult['subdomain'] = subdomain
        try:
            for qtype in ['A', 'CNAME']:

                answers = dnsResolver.resolve(subdomain, qtype)

                if answers.rrset is None:
                    pass

                elif answers.rdtype == 1:
                    a_records = [str(i) for i in answers.rrset]
                    dnsResult["A"] = a_records

                elif answers.rdtype == 5:
                    cname_records = [str(i) for i in answers.rrset]
                    dnsResult["CNAME"] = cname_records

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except dns.exception.DNSException:
            pass

        except Exception as e:
            print(colored("[!] Error while resolving subdomain \n[!] {}".format(e), "red"))

        finally:
            if dnsResult.get('A') is not None and dnsResult.get('CNAME') is not None:
                self.notify(message=dnsResult)

    def notify(self, message):
        """ send message via slack Or Telegram """
        if self.slack:
            self.sendNotification.slack(notificationTemplate(message))

        if self.telegram:
            self.sendNotification.telegrame(notificationTemplate(message))

    def compaire(self, subdomians):
        """ Compate a list of given subdomains and :return: return new subdomains """

        try:
            domain = subdomians.get('domain')
            newsubDomain = subdomians.get('subdomains')
            target = self.db._findOne(domain=domain)  # get all subdomian by domian name

            if target is None:
                print(colored("[+] new target {domain} : {length} subdomain ".format(domain=domain, length=len(newsubDomain)),"green"))
                self.db._add(target=subdomians)
            else:
                if len(newsubDomain) > 0:
                    oldSubdomain = target.get('subdomains')
                    diff = [x for x in newsubDomain if x not in oldSubdomain]
                    if len(diff) > 0:
                        self.db._update(domain, diff)
                        print(colored("[+] {0} new subdomains found for {1}".format(len(diff), domain), "green"))
                        for subdomian in diff:
                            pthread = threading.Thread(target=self.scanSubdomain, args=(subdomian,))
                            pthread.start()

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while comparing result \n[!] {}".format(e), "red"))

    def add(self, domain):
        """ Add new domain to Monitoring """
        if self.db._findOne(domain=domain) is None:
            self.compaire(self.getdomain(domain=domain))
        else:
            print(colored("[+] {} already exist in database".format(domain), "green"))

    def readfile(self, file):
        return open(file, 'r').readlines()

    def importDomainsFromFile(self, file):
        """ import list of domains from a text file """
        try:
            domains = self.readfile(file)
            for i in domains:
                domain = i.strip()
                if domain:
                    print(colored("[+] import : ", "blue") + colored(domain, 'green', attrs=['reverse']))
                    t = threading.Thread(target=self.add, args=(domain,))
                    t.start()

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] {0}".format(e), "red"))

    def listAllDomains(self):
        """ list all domain monitoring in DB """
        for domain in self.db._findAll():
            print(colored("[+] {}".format(domain.get('domain')), "green"), colored("{0}".format(len(domain.get('subdomains'))), "green"))

    def getSubdomains(self, domain):
        """ return a list of subdomain for given domain """
        target = self.db._findOne(domain=domain)
        if target is not None:
            target = target.get('subdomains')
            for i in target: print(i)
        else:
            print(colored("[+] domain {} not exist in database".format(domain), "green"))

    def deleteDomain(self, domain):
        """ Delete domain from database """
        confirm = input('Are you sure want to delete [yes / no] : ')
        if confirm == 'yes' or confirm == 'y':
            self.db._delete(domain=domain)
            print(colored("[+] delete {} from database".format(domain), "blue"))

    def export(self):
        """ export all subdomain to text file """
        try:
            total = 0
            all = self.db._findAll()
            with open("export-" + getCurrentTime() + ".txt", "w") as file:
                for domain in all:
                    total = total + len(domain.get('subdomains'))
                    for subdomain in domain.get('subdomains'):
                        file.write(subdomain + "\n")
            file.close()
            print(colored("[+] Export {} from database ".format(total), "green"))

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as error:
            print(colored("[!] {0}".format(error), "red"))

    def monitor(self):
        """ Monitor All domains in database """
        try:
            for domain in self.db._findAll():
                print(colored("[+] Checking : ", "blue") + colored(domain.get('domain'), 'green', attrs=['reverse']))
                thread = threading.Thread(target=self.compaire, args=(self.getdomain(domain.get('domain')),))
                thread.start()
        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as error:
            print(colored("[!] {0}".format(error), "red"))

    def initArgparse(self):
        parser = argparse.ArgumentParser(description='Simple tools to monitoring new subdomains')

        parser.add_argument("-m", "--monitor", help="looking for new subdomain", type=bool, metavar='', required=False,
                            nargs='?', const=True)

        parser.add_argument("-a", "--add", help="Domain to monitor. E.g: domain.com", type=str, metavar='',
                            required=False)

        parser.add_argument("-l", "--listdomains", help="list all domain on database", type=bool, metavar='',
                            required=False,
                            const=True, nargs='?')

        parser.add_argument("-i", "--importfile", help="import Domains From File", type=str, metavar='',
                            required=False)

        parser.add_argument("-L", "--listsubdomains", help="list all domain on for domain", type=str, metavar='',
                            required=False)

        parser.add_argument("-d", "--delete", help="disable for monitoring", type=str, metavar='', required=False)

        parser.add_argument("-e", "--export", help="export all subdomains for all domains into single file", type=bool, metavar='',
                            required=False,
                            const=True, nargs='?')

        parser.add_argument("-s", "--slack", help="send notification via slack", type=bool, metavar='', required=False,
                            const=True, nargs='?')

        parser.add_argument("-t", "--telegram", help="send notification via telegram", type=bool, metavar='',
                            required=False,
                            const=True, nargs='?')

        return parser.parse_args()

    def main(self, args):

        if args.slack: self.slack = True

        if args.telegram: self.telegram = True

        if args.listdomains: self.listAllDomains()

        elif args.listsubdomains: self.getSubdomains(domain=args.listsubdomains)

        elif args.delete: self.deleteDomain(domain=args.delete)

        elif args.add: self.add(domain=args.add)

        elif args.importfile:  self.importDomainsFromFile(file=args.importfile)

        elif args.export: self.export()

        elif args.monitor: self.monitor()


def banner():
    BANNER = """

        ███╗   ███╗███╗   ██╗███████╗
        ████╗ ████║████╗  ██║██╔════╝
        ██╔████╔██║██╔██╗ ██║███████╗
        ██║╚██╔╝██║██║╚██╗██║╚════██║
        ██║ ╚═╝ ██║██║ ╚████║███████║
        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝
    ## {0}
    ## {1}
    ## version {2}
    """
    print(colored(BANNER.format("Monitor New Subdomains", "@omarelfarsaoui", version), 'red'))


if __name__ == "__main__":
    try:
        banner()
        subdomainMonitoring = SubDomainMonitoring()
        args = subdomainMonitoring.initArgparse()
        subdomainMonitoring.main(args)

    except KeyboardInterrupt:
        print(colored("[-] Ctrl+c detected", "yellow"))
        exit(0)

    except Exception as error:
        raise Exception(error)
        print(colored("[!] {0}".format(error), "red"))

