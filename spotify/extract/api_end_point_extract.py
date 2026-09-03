
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
    data_all = []

    top_artists_tracks = []
    url = f"{BASE_URL}/me/top/{param}"
    params = {"limit": 50, "time_range": "long_term"}

    try:
        while url:
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            top_artists_tracks.extend(data["items"])
            # data_all.append(data)

            print(f"Fetched {len(data['items'])} records")

            url = data["next"]
            params = None

        return top_artists_tracks
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user's top {param}: {e}")
        raise


def get_user_playlists(access_token):

    headers = {"Authorization": f"Bearer {access_token}"}
    data_all = []
    session = make_session_with_retries()

    user_playlists = []
    user_playlist_items = []
    playlist_url = f"{BASE_URL}/me/playlists"
    
    params_outer = {"limit": 50}

    try:
        while playlist_url:
            response = session.get(playlist_url, headers=headers, params=params_outer)
            response.raise_for_status()

            playlist_data = response.json()
            user_playlists.extend(playlist_data["items"])
            ##data_all.append(data)

            print(f"Fetched {len(playlist_data['items'])} records")

            print("\n")

            for playlist in playlist_data["items"]:

                playlist_id = playlist["id"]
                print(f"The playlist id is {playlist_id}")

                playlist_items_url = f"{BASE_URL}/playlists/{playlist_id}/items"
                params_inner = {"limit": 50}

                while playlist_items_url:

                    try:
                        response = session.get(playlist_items_url, headers=headers, params=params_inner)
                        response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        if response.status_code == 403:
                            print(f"Skipping playlist {playlist_id} — not accessible")
                            break
                        raise

                    data = response.json()

                    for item in data["items"]:
                        item["playlist_id"] = playlist_id

                    user_playlist_items.extend(data["items"])
                    print(f"Fetched {len(data['items'])} records")
                    playlist_items_url = data["next"]
                    params_inner=None

            playlist_url = playlist_data["next"]
            params_outer = None

        return user_playlist_items, user_playlists
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user's playlists: {e}")
        raise










