
from auth.spotify_auth import build_authorization_url, get_access_token
from auth.token_manager import get_access_token_via_refresh_token
from extract.api_end_point_extract import get_recent_tracks, get_users_saved_tracks, get_users_top_artists, get_users_top_tracks, get_user_playlists
from extract.flatten_data import flatten_recent_tracks, flatten_saved_tracks, flatten_user_top_artists, flatten_user_top_tracks, flatten_user_playlist_items, flatten_user_playlist
from load.snowflake_loader import user_recent_tracks_load_to_snowflake, user_saved_tracks_load_to_snowflake 
from config import REFRESH_TOKEN
from utils.file_utils import save_json 

# url = build_authorization_url()
# print(url)

# code = input("Paste authorization code: ")

# token_response = get_access_token(code)


def main():

    token_response = get_access_token_via_refresh_token(REFRESH_TOKEN)

    

    # Extract Operation : Extract data from all the spotify end points 

    # calling recent-track data end point.

    tracks = get_recent_tracks(token_response["access_token"])
    save_json(tracks, "data/recent_tracks.json")
    flatten_recent_tracks()

    # calling the users saved tracks list. 
 
    user_saved_songs = get_users_saved_tracks(token_response["access_token"])
    save_json(user_saved_songs, "data/user_saved_tracks.json")
    flatten_saved_tracks()

    # calling user top artist and tracks

    users_top_artists = get_users_top_artists(token_response["access_token"],"artists")
    save_json(users_top_artists, "data/user_top_artists.json")
    flatten_user_top_artists()

    users_top_tracks = get_users_top_tracks(token_response["access_token"],"tracks")
    save_json(users_top_tracks, "data/user_top_tracks.json")
    flatten_user_top_tracks()

    # calling user playlist and  items in it.

    user_playlist_items, user_playlists = get_user_playlists(token_response["access_token"])
    save_json(user_playlists, "data/user_playlist.json")
    save_json(user_playlist_items, "data/user_playlist_tracks.json")
    flatten_user_playlist_items()
    flatten_user_playlist()

    # Loading Operation : Load data into the snowflake RAW tables
    user_recent_tracks_load_to_snowflake()
    user_saved_tracks_load_to_snowflake()

    

if __name__ == "__main__":
    main()
