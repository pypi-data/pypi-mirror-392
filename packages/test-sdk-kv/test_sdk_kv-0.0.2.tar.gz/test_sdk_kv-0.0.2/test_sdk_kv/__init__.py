import requests

class Client:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def _headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers


    def k_search(self, json=None, **kwargs):
        k_search_url = 'http://95.217.25.159:5000/api/doc/k_search'
        resp = requests.post(k_search_url, json=json, headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()["data"]

