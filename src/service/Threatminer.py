from requests import get


class Threatminer:
	"""
	  get subdomains from https://threatminer/

	"""
	
	def get_subdomains(self, domain):
		""" get subdomains from Threatminer API """
		
		url = f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=5"
		res = get(url=url, timeout=30, verify=False)
		res.raise_for_status()
		resp = res.json()
		if resp.get('results') is not None:
			return resp.get('results')
		
		return []
