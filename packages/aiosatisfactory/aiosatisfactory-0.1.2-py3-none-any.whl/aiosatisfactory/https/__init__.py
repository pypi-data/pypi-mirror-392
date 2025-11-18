import aiohttp
from .api import ApiEndpoints

class HttpsAPI:

    def __init__(self, self_signed_certificate: bool, host: str, port: int, session: aiohttp.ClientSession, api_token: str):
        self._host = host
        self._port = port
        self._api_token = api_token
        self._headers = {
            'content-type': 'application/json',
        }

        if api_token:
            self._headers["Authorization"] = f"Bearer {self._api_token}"

        self._url = f"https://{self._host}:{self._port}/api/v1"

        self._api = ApiEndpoints(session, self._url, self._headers, self_signed_certificate)
    
    @property
    def api_token(self, new_token: str = "") -> str:
        if new_token:
            self._api_token = new_token
            self._headers["Authorization"] = f"Bearer {self._api_token}"
        return self._api_token

    @property
    def api(self) -> ApiEndpoints:
        return self._api
