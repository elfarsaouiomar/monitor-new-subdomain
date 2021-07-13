from datetime import datetime
from jinja2 import Template

def getCurrentTime():
    """ Retun current time eg : 2021-07-12-01-30-11 """
    return datetime.now().strftime("%Y-%m-%d-%I-%M-%S")

def notificationTemplate(subdomain):
    template = """New Subdomain was discovered {% if subdomain %}\nsubdomain   :  {{subdomain}}{% endif %}{% if A %}\nA record    : {% for item in A %} {{ item }} {% endfor %} {% endif %}{% if CNAME %}\nCNAME record: {% for item in CNAME %} {{ item }} {% endfor %}{% endif %}\n\n"""
    tm = Template(template)
    return tm.render(subdomain=subdomain.get('subdomain'), A=subdomain.get('A'), CNAME=subdomain.get('CNAME'))
