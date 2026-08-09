
import requests
from config import BASE_URL


def get_recent_tracks(access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        f"{BASE_URL}/me/player/recently-played",
        headers=headers,
        params={"limit": 50},
    )

    response.raise_for_status()

    return response.json()