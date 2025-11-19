import requests

class Client:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["api_key"] = self.api_key
        return headers

    def _url(self, path: str):
        if path.startswith("http"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs):
        resp = requests.get(self._url(path), headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json=None, **kwargs):
        resp = requests.post(self._url(path), json=json, headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, json=None, **kwargs):
        resp = requests.put(self._url(path), json=json, headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, **kwargs):
        resp = requests.delete(self._url(path), headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()
