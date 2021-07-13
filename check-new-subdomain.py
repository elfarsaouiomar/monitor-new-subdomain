#!/usr/bin/env python
# I don't believe in the license, you can do whatever you like

version = "1.1"


import argparse
import threading
from json import loads
import dns.resolver
import requests.packages.urllib3
from jinja2 import Template
from requests import get
from termcolor import colored

from src.ConfigDB import ConfigDB
from src.Config import resolverList
from src.Functions import getCurrentTime
from src.Notifications import Notifications

# disable requests warnings
requests.packages.urllib3.disable_warnings()

class SubDomainMonitoring:
    db = ConfigDB()
    sendNotification = Notifications()
    slack = telegram = saveToFile = False

    def parseCrtResponse(self, subdomains):
        """
        :return: list of subomian (sort, clean, uniq)
        """
        newSubdomains = list()
        try:
            for i in subdomains:
                listsubdomians = i.split('\n')
                for subDomain in listsubdomians:
                    if subDomain not in newSubdomains:
                        subDomain = subDomain.replace("*.", "")
                        newSubdomains.append(subDomain)

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] error on parsing crt response \n [!] {}".format(e), "red"))

        return newSubdomains

    def getFromThreatminer(self, domain):
        url = "https://api.threatminer.org/v2/domain.php?q={}&rt=5".format(domain)
        res = get(url)
        if res.status_code != 200:
            return []
        resp = res.json()
        if resp.get('results') is not None:
            return resp.get('results')
        return []

    def getFormSublister(self, domain):
        resp = get("https://api.sublist3r.com/search.php?domain={}".format(domain)).json()
        if resp is not None:
            return resp
        return []

    def getdomain(self, domain):
        resultSubdomains = dict()
        resultSubdomains['domain'] = domain
        resultSubdomains["subdomains"] = list(set(
            self.getFormSublister(domain=domain) + self.getFromCrt(domain=domain) + self.getFromThreatminer(
                domain=domain)))

        return resultSubdomains

    def getFromCrt(self, domain):
        """
            take domain as string
            check crt.sh for
            retrun a list of subdomain
        """
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
            print(colored("[!!] Error while resolving subdomain \n[!] {}".format(e), "red"))

        finally:
            return dnsResult

    def notify(self, message):
        """
        send message via slack Or Telegram
        :param message:
        """
        if self.slack:
            self.sendNotification.slack(message)

        if self.telegram:
            self.sendNotification.telegrame(message)

    def compaire(self, subdomians):
        """
        take a list of subdomain
        call getFromDb => get all subdomain from DB as list
        compaire the two list

        :param subdomians: list of subdomain
        :return: return new subdomain
        """

        try:
            domain = subdomians.get('domain')
            newsubDomain = subdomians.get('subdomains')

            target = self.db._findOne(domain=domain)  # get all subdomian by domian name
            if target is None:
                print(colored(
                    "[+] new target {domain} : {length} subdomain ".format(domain=domain, length=len(newsubDomain)),
                    "green"))
                self.db._add(target=subdomians)

            else:
                if len(newsubDomain) > 0:
                    oldSubdomain = target.get('subdomains')
                    diff = [x for x in newsubDomain if x not in oldSubdomain]

                    if len(diff) > 0:
                        self.db._update(domain, diff)
                        print(colored("[+] {0} new subdomains found for {1}".format(len(diff), domain), "green"))
                        victim = []
                        for subdomian in diff:
                            res = self.scanSubdomain(subdomian)
                            victim.append(res)
                        self.telegrameTemplate(subdomainlist=victim)

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while comparing result \n[!] {}".format(e), "red"))

    def telegrameTemplate(self, subdomainlist):
        template = """New subdomain {% if subdomain %}\nsubdomain : {{subdomain}}{% endif %}{% if A %}\nA record : {{A}}{% endif %}{% if cname %}\nCNAME record: {{cname}}{% endif %}"""
        for i in subdomainlist:
            tm = Template(template)
            msg = tm.render(subdomain=i.get('subdomain'), A=i.get('A'), cname=i.get('CNAME'))
            self.notify(msg)

    def add(self, domain):
        """
        add new domain to Monitoring
        :param domain:
        :return:
        """
        if self.db._findOne(domain=domain) is None:
            self.compaire(self.getdomain(domain=domain))
        else:
            print(colored("[+] {} already exist in database".format(domain), "green"))

    def readfile(self, file):
        return open(file, 'r').readlines()

    def importDomainsFromFile(self, file):
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
            print(colored("[!] {0}".format(error), "red"))

    def listAllDomains(self):
        """
        list all domain monitoring in DB
        :return:
        """
        for domain in self.db._findAll():
            print(colored("[+] {}".format(domain.get('domain')), "green"),
                  colored("{0}".format(len(domain.get('subdomains'))), "green"))

    def getSubdomains(self, domain):
        target = self.db._findOne(domain=domain)
        if target is not None:
            target = target.get('subdomains')
            for i in target:
                print(i)
        else:
            print(colored("[+] domain {} not exist in database".format(domain), "green"))

    def deleteDomain(self, domain):
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
        parser = argparse.ArgumentParser(description='Simple tools to monitoring new subdomain')

        parser.add_argument("-m", "--monitor", help="looking for new subdomain", type=bool, metavar='', required=False,
                            nargs='?', const=True)

        parser.add_argument("-sn", "--saveNewSubdomain", help="save new subdomain to file", type=bool, metavar='', required=False,
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

        if args.saveNewSubdomain: self.saveToFile = True

        if args.listdomains: self.listAllDomains()

        elif args.listsubdomains: self.getSubdomains(domain=args.listsubdomains)

        elif args.delete: self.deleteDomain(domain=args.delete)

        elif args.add: self.add(domain=args.add)

        elif args.importfile:  self.importDomainsFromFile(file=args.importfile)

        elif args.export: self.export()

        else: self.monitor()


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
    print(colored(BANNER.format("Monitor New Subdomain", "@omarelfarsaoui", version), 'red'))


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
        print(colored("[!] {0}".format(error), "red"))

