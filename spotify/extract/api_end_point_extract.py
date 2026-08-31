
import requests
import json
from config import BASE_URL
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=3,              # try up to 3 times
        backoff_factor=2,      # wait 2s, then 4s, then 8s between retries
        status_forcelist=[429, 500, 502, 503, 504],  # retry on these HTTP errors too
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def get_recent_tracks(access_token):

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        all_tracks = []

        url = f"{BASE_URL}/me/player/recently-played"

        try:

            while url:
                response = requests.get(
                url,
                headers=headers,
                params={"limit": 10},
                )

                response.raise_for_status()

                data = json.loads(response.text) # parse json into py dic.
                all_tracks.extend(data["items"])

                print(f"Fetched {len(data['items'])} records")

                url = data["next"]
                params = None 

            return all_tracks

        except requests.exceptions.RequestException as e:
             print(f"Failed to fetch recently played tracks: {e}")
             raise


def get_users_saved_tracks(access_token):

    headers = {
          "Authorization": f"Bearer {access_token}"
     }

    saved_tracks = []
    data_all = []

    url = f"{BASE_URL}/me/tracks"

    try: 

        while url:
            response = requests.get(
                url,
                headers=headers,
                params={"limit": 25},
            )

            response.raise_for_status()

            data = data = json.loads(response.text) # parse json into py dic.
            # data_all.append(data)
            saved_tracks.extend(data["items"])

            print(f"fetched {len(data['items'])} records")

            url = data["next"]
            params = None

        return saved_tracks

    except requests.exceptions.RequestException as e:
         print(f"Failed to fetch user's saved tracks: {e}")
         raise


def get_users_top_artists(access_token, param):

    headers = {
          "Authorization": f"Bearer {access_token}"
     }

    top_artists_tracks = []
    data_all = []

    url = f"{BASE_URL}/me/top/{param}"
    params = {
              "limit": 50, 
              "time_range": "long_term"}

    try: 

        while url:
            response = requests.get(
                url,
                headers=headers,
                params=params,
            )

            response.raise_for_status()

            data = data = json.loads(response.text) # parse json into py dic.
            # data_all.append(data)
            top_artists_tracks.extend(data["items"])

            print(f"fetched {len(data['items'])} records")

            url = data["next"]
            params = None

        return top_artists_tracks

    except requests.exceptions.RequestException as e:
         print(f"Failed to fetch user's top tracks/artists: {e}")
         raise


def get_users_top_tracks(access_token, param):
    headers = {"Authorization": f"Bearer {access_token}"}
    session = make_session_with_retries()

    top_artists_tracks = []
    url = f"{BASE_URL}/me/top/{param}"
    params = {"limit": 50, "time_range": "long_term"}

    try:
        while url:
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            top_artists_tracks.extend(data["items"])

            print(f"Fetched {len(data['items'])} records")

            url = data["next"]
            params = None

        return top_artists_tracks

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user's top {param}: {e}")
        raise







