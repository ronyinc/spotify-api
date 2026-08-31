
from auth.spotify_auth import build_authorization_url, get_access_token
from auth.token_manager import get_access_token_via_refresh_token
from extract.api_end_point_extract import get_recent_tracks, get_users_saved_tracks, get_users_top_artists, get_users_top_tracks
from extract.flatten_data import flatten_recent_tracks, flatten_saved_tracks
from config import REFRESH_TOKEN
from utils.file_utils import save_json 

# url = build_authorization_url()
# print(url)

# code = input("Paste authorization code: ")

# token_response = get_access_token(code)

token_response = get_access_token_via_refresh_token(REFRESH_TOKEN)

# calling recent-track data end point.

# tracks = get_recent_tracks(token_response["access_token"])
# save_json(tracks, "data/recent_tracks.json")
# flatten_recent_tracks()

# calling the users saved tracks list. 

# user_saved_songs = get_users_saved_tracks(token_response["access_token"])
# save_json(user_saved_songs, "data/user_saved_tracks.json")
# flatten_saved_tracks()

# users_top_artists = get_users_top_artists(token_response["access_token"],"artists")
# save_json(users_top_artists, "data/user_top_artists.json")

users_top_tracks = get_users_top_tracks(token_response["access_token"],"tracks")
save_json(users_top_tracks, "data/user_top_tracks.json")

