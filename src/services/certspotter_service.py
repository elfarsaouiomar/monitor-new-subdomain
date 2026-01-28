from re import match
from requests import get, RequestException


class CertSpotter:
    """
    get subdomains from certspotter.com
    """

    def get_subdomains(self, domain) -> list:
        """get subdomains from certspotter"""
        url = "https://api.certspotter.com/v1/issuances"
        params = {
            "domain": domain,
            "include_subdomains": "true",
            "expand": "dns_names",
            "limit": 1000,
        }

        subdomains = set()

        try:
            response = get(url, params=params, timeout=60)

            # Rate limit reached
            if response.status_code == 429:
                raise RequestException("Rate limit reached")

            if response.status_code != 200:
                raise RequestException(
                    f"Error fetching data from CertSpotter: {response.status_code}"
                )

            data = response.json()
            for entry in data:
                for name in entry.get("dns_names", []):
                    if name.endswith(domain) and not match(r"^[0-9\.]+$", name):
                        subdomains.add(name)

        except RequestException:
            raise Exception("Error connecting to CertSpotter API")

        return self.parse_response(subdomains=subdomains)

    def parse_response(self, subdomains) -> list:
        """Parse certspotter response and return list of subdomains (sort, clean, uniq)"""
        results = set()
        for sub in subdomains:
            results.add(sub.replace("*.", "").replace("@", "."))
        return sorted(results)
