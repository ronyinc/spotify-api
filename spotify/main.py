
from auth.spotify_auth import build_authorization_url, get_access_token, get_access_token_via_refresh_token
from extract.recent_tracks import get_recent_tracks
from config import REFRESH_TOKEN
from utils.file_utils import save_json 

# url = build_authorization_url()
# print(url)

# code = input("Paste authorization code: ")

# token_response = get_access_token(code)

token_response = get_access_token_via_refresh_token(REFRESH_TOKEN)


tracks = get_recent_tracks(token_response["access_token"])

save_json(tracks, "data/recent_tracks.json")