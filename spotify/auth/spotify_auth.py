
from urllib.parse import urlencode
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, TOKEN_URL 
import requests



def build_authorization_url():

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }

    auth_url = (
    "https://accounts.spotify.com/authorize?"
    + urlencode(params)
    )

    return auth_url

def get_access_token(code):

    payload = {
				"grant_type": "authorization_code",
				"code": code,
				"redirect_uri": REDIRECT_URI,
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET
			}
    
    response = requests.post(TOKEN_URL, data=payload)

    print(response.status_code)
    # print(response.text)

    response.raise_for_status()

    return response.json()
    


        


