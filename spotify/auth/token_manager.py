from urllib.parse import urlencode
from config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL
import requests


def get_access_token_via_refresh_token(refresh_token):

    payload = {
				"grant_type": "refresh_token",
				"refresh_token": refresh_token,
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET
			}
    
    response = requests.post(TOKEN_URL, data=payload)

    # print(response.status_code)
    # print(response.text)

    response.raise_for_status()

    return response.json()