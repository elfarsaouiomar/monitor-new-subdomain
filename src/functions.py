from datetime import datetime
from jinja2 import Template
import logging
from sys import stdout

def get_current_time():
    """ Retun current time eg : 2021-07-12-01-30-11 """
    return datetime.now().strftime("%Y-%m-%d-%I-%M-%S")

def notification_template(subdomain):
    template = """New Subdomain was discovered {% if subdomain %}\nsubdomain   :  {{subdomain}}{% endif %}{% if A %}\nA record    : {% for item in A %} {{ item }} {% endfor %} {% endif %}{% if CNAME %}\nCNAME record: {% for item in CNAME %} {{ item }} {% endfor %}{% endif %}\n\n"""
    tm = Template(template)
    return tm.render(subdomain=subdomain.get('subdomain'), A=subdomain.get('A'), CNAME=subdomain.get('CNAME'))


def custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-2s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('logs/logs.log')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

def raise_for_status(response, status_code):
    """ 
        Todo: write a function that used to check if status code equal to 200 and print (error message otherwise)
    """
    pass