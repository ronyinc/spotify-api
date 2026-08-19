
import requests
import json
from config import BASE_URL


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
