from requests import get
from re import match


class Crtsh:
	"""
	  get subdomains from https://crt.sh/

	"""
	
	def get_subdomains(self, domain) -> list:
		""" get subdomain from crt.sh """
		url = f"https://crt.sh/?q=%25.{domain}&output=json"
		response = get(url, timeout=60, verify=False)
		
		if response.status_code == 200:
			subdomains = set()
			data = response.json()
			for entry in data:
				name_value = entry["name_value"]
				if not match(r"^[0-9\.]+$", name_value):
					subdomains.add(name_value)
			return self.parse_response(subdomains=subdomains)
		return []
	
	def parse_response(self, subdomains) -> list:
		""" Parse crt.sh response and return list of subdomains (sort, clean, uniq) """
		
		results = set()
		for i in subdomains:
			list_subdomains = i.split('\n')
			for sub_domain in list_subdomains:
				results.add(sub_domain.replace("*.", "").replace("@", "."))
		return list(results)
