#!/usr/bin/env python

version = "1.0"

import argparse
from requests import post, get
from json import loads, dumps
import logging
import dns.resolver
from pymongo import MongoClient
from config import *
from termcolor import colored
import threading

class Notify:
    """
    send message via Telegrame
    """

    def viaTelegram(self, message):

        try:
            telegramUrl = "https://api.telegram.org/bot{0}/sendMessage".format(telegramToken)
            req  = post(telegramUrl, params={'text': dumps(message), 'chat_id': chatId, 'parse_mode': 'Markdown'},
                 headers={'Content-Type': 'application/json'})
            if req.status_code != 200:
                print(colored("[!] error wile sending Message \n[!] status code : {0}".format(req.status_code),  "red"))
                
        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "red"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while sending slack message \n [!] {}".format(e), "red"))
    """
    send message via slack
    """

    def viaSlack(self, message):
        try:
            req = post(WHslack, json={'text': ':new: {0}'.format(message)}, headers={'Content-Type': 'application/json'})
            if req.status_code != 200:
                print(colored("[!] error wile sending Message \n[!] status code : {0}".format(req.status_code),  "red"))
            if req.status_code == 429:
                print(colored("[!] Api Rate limit : ",  "red"))
        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "blue"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while sending slack message \n [!] {}".format(e), "red"))


class ConnToDb:
    """
    Connection to mongodb 
    """
    client = MongoClient(dbHost, dbPort)
    db = client['MonitoringSubdomain']
    collection = db['subdomains']

    def _findAll(self):
        """
        get all subdomain
        :return:
        """
        return self.collection.find()

    def _add(self, target):
        """
        take two arg
        domian string
        newsubdomian list of newSubdomian
        """
        self.collection.insert_one(target)

    def _update(self, domain, newSubbdomain):
        """
        update document in DB
        :param domain:
        :return:
        """
        self.collection.update_one({"domain": domain}, {"$pushAll": {"subdomains": newSubbdomain}})

    def _findOne(self, domain):
        """
        :param domain: take domain as params
        :return: return Object of domain
        """
        return self.collection.find_one({"domain": domain})

    def _delete(self, domain):
        """
        delete domain name from database
        :param domain: domain name
        :return:
        """
        self.collection.find_one_and_delete({"domain": domain})

    def _close(self):
        """
         close  connection
        :return:
        """
        self.client.close()


class SubDomainMonitoring:
    db = ConnToDb()
    sendNotification = Notify()
    slack = False
    telegram = False

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
            print(colored("[!] Ctrl+c detected", "red"))
            exit(0)

        except Exception as e:
            print(colored("[!] error on parsing crt response \n [!] {}".format(e), "red"))

        return newSubdomains

    def getdomain(self, domain):
        """
            take domain as string
            check crt.sh for
            retrun a list of subdomain
        """
        resultSubdomains = dict()
        resultSubdomains['domain'] = domain
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
                resultSubdomains["subdomains"] = self.parseCrtResponse(sorted(subdomains))
            return resultSubdomains

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "red"))
            exit(0)

        except Exception as e:
            print(colored("[!] error while requesing crt \n [!] {}".format(e), "red"))

        return resultSubdomains

    def scanSubdomain(self, subdomain):
        """
        """
        dnsResolver = dns.resolver.Resolver()
        dnsResolver.nameservers = ['8.8.8.8', '8.8.4.4']

        dnsResult = dict()
        dnsResult['new subdomains '] = subdomain
        try:
            for qtype in ['A', 'CNAME']:
                answers = dns.resolver.resolve(subdomain, qtype, raise_on_no_answer=False)

                if answers.rrset is None:
                    pass

                elif answers.rdtype == 1:
                    a_records = [str(i) for i in answers.rrset]
                    dnsResult["A"] = a_records[0]

                elif answers.rdtype == 5:
                    cname_records = [str(i) for i in answers.rrset]
                    dnsResult["CNAME"] = cname_records[0]

            #target=self.notify, args=(dnsResult,)
            
            self.notify(dnsResult)

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "red"))
            exit(0)

        except dns.exception.DNSException:
            pass

        except Exception as e:
            print(colored("[!] error on resolving subdomain \n [!] {}".format(e), "red"))

        return dnsResult

    def notify(self, message):
        """
        send message via slack Or Telegram
        :param message:
        """
        if self.slack:
            self.sendNotification.viaSlack(message)

        if self.telegram:
            self.sendNotification.viaTelegram(message)

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
                print(colored("[+] Insert  subdomain {0} for {1}".format(len(newsubDomain), domain), "green"))
                self.db._add(target=subdomians)

            else:
                oldSubdomain = target.get('subdomains')
                if len(newsubDomain) != 0:
                    diff = [x for x in oldSubdomain + newsubDomain if x not in oldSubdomain or x not in newsubDomain]

                    diffLength = len(diff)

                    if diffLength == 0:
                        message = "unfortunately i don't found any new subdomain for {0} good look next time".format(domain)
                        self.notify(message)

                    else:
                        self.db._update(domain, diff)
                        print(colored("[+] Update new {0} subdomain ".format(diffLength), "green"))
                        for subdomian in diff:
                            self.scanSubdomain(subdomian)

        except Exception as e:
            print(colored("[!] error while comparing result \n[!] {}".format(e), "red"))

    def add(self, domain):
        """
        add new domain to Monitoring
        :param domain:
        :return:
        """
        self.compaire(self.getdomain(domain=domain))

    def listAllDomains(self):
        """
        list all domain monitoring in DB
        :return:
        """
        for domain in self.db._findAll():
            print(colored("[+] {}".format(domain.get('domain')), "green"))

    def getSubdomains(self, domain):
        target = self.db._findOne(domain=domain)
        target = target.get('subdomains')
        for i in target:
            print(i)

    def deleteDomain(self, domain):
        self.db._delete(domain=domain)
        print(colored("[+] delete {} from database".format(domain), "blue"))

    def monitor(self):
        for domain in self.db._findAll():
            print(colored("[+] Checking : ", "blue")+ colored(domain.get('domain'), 'green', attrs=['blink']))
            thread = threading.Thread(target=self.compaire, args=(self.getdomain(domain.get('domain')),))
            thread.start()

            #thread.join()
            #result = self.getdomain(domain.get('domain'))
            #self.compaire(result)

    def initArgparse(self):
        parser = argparse.ArgumentParser(description='Simple tools to monitoring new subdomain')

        parser.add_argument("-m", "--monitor", help="looking for new subdomain", type=bool, metavar='', required=False,
                            nargs='?', const=True)
        parser.add_argument("-a", "--add", help="Domain to monitor. E.g: domain.com", type=str, metavar='',
                            required=False)

        parser.add_argument("-l", "--listdomains", help="list all domain on database", type=bool, metavar='', required=False,
                            const=True, nargs='?')

        parser.add_argument("-L", "--listsubdomains", help="list all domain on for domain", type=str, metavar='', required=False)

        parser.add_argument("-d", "--delete", help="disable for monitoring", type=str, metavar='', required=False)

        parser.add_argument("-s", "--slack", help="send notification via slack", type=bool, metavar='', required=False,
                            const=True, nargs='?')
        parser.add_argument("-t", "--telegram", help="send notification via telegram", type=bool, metavar='',
                            required=False,
                            const=True, nargs='?')

        return parser.parse_args()

    def main(self, args):

        if args.slack:
            self.slack = True

        if args.telegram:
            self.telegram = True

        if args.listdomains:
            self.listAllDomains()

        elif args.listsubdomains:
            self.getSubdomains(domain=args.listsubdomains)

        elif args.delete:
            self.deleteDomain(domain=args.delete)

        elif args.add:
            self.add(args.add)

        else:
            self.monitor()


def banner():
    BANNER = """

        ███╗   ███╗███╗   ██╗███████╗
        ████╗ ████║████╗  ██║██╔════╝
        ██╔████╔██║██╔██╗ ██║███████╗
        ██║╚██╔╝██║██║╚██╗██║╚════██║
        ██║ ╚═╝ ██║██║ ╚████║███████║
        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝                       
    # {0}
    # {1}
    # version {2}                         
    """
    print(colored(BANNER.format("Monitor New Subdomain","@omarelfarsaoui",version),'red'))


if __name__ == "__main__":
    try:
        banner()
        subdomainMonitpring = SubDomainMonitoring()
        args = subdomainMonitpring.initArgparse()
        subdomainMonitpring.main(args)
    
    except KeyboardInterrupt:
        print(colored("[!] Ctrl+c detected", "blue"))
        exit(0)

    except Exception as error:
        print(colored("[!] {0}".format(error), "red"))