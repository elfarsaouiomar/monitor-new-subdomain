#!/usr/bin/env python
# I don't believe in the license, you can do whatever you like
<<<<<<< HEAD
import asyncio
=======

>>>>>>> 1ee0a7b (* refactor the code)
from random import choice
from requests import exceptions
from termcolor import colored
import requests.packages.urllib3

from src.mns import SubDomainMonitoring
from src.functions import custom_logger

# disable requests warnings
requests.packages.urllib3.disable_warnings()

# Create and configure logger
logger = custom_logger("Main")


def show_banner():
    colors = ['red', 'green', 'blue', 'yellow', 'magenta']
    version = "2.0"
    banner = f"""

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
    print(colored(banner, choice(colors)))


def main():
    try:
        show_banner()
        subdomains_monitoring = SubDomainMonitoring()
        args = subdomains_monitoring.init_args()
        subdomains_monitoring.main(args)

    except exceptions.HTTPError as http_error:
        logger.error(f"[!] Http Error: {http_error}")

    except exceptions.ConnectionError as connection_error:
        logger.error(f"[!] Error Connecting: {connection_error}")

    except exceptions.Timeout as timeout_error:
        logger.error(f"[!] Timeout Error: {timeout_error}")

    except exceptions.RequestException as request_error:
        logger.error(f"[!] Ops: Something Else: {request_error}")

    except KeyboardInterrupt:
        logger.info("[!] Ctrl+c detected")
        exit(0)

    except Exception as error:
        logger.error(error)
        exit(1)


if __name__ == "__main__":
    main()
