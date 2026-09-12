from urllib.parse import urlencode
from config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def get_access_token_via_refresh_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    session = make_session_with_retries()
    response = session.post(TOKEN_URL, data=payload)

    response.raise_for_status()
    return response.json()