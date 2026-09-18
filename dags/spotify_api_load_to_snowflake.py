
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator 
from spotify.auth.token_manager import get_access_token_via_refresh_token
from spotify.utils.file_utils import save_json
from spotify.config import REFRESH_TOKEN 

from spotify.extract.api_end_point_extract import (
    get_recent_tracks,
    get_users_saved_tracks,
    get_users_top_tracks,
    get_users_top_artists,
    get_user_playlists
)

from spotify.extract.flatten_data import (
    flatten_recent_tracks,
    flatten_saved_tracks,
    flatten_user_top_tracks,
    flatten_user_top_artists,
    flatten_user_playlist_items,
    flatten_user_playlist

)

from spotify.load.snowflake_loader import (
    user_recent_tracks_load_to_snowflake,
    user_saved_tracks_load_to_snowflake,
    user_top_tracks_load_to_snowflake,
    user_top_artist_load_to_snowflake,
    user_playlist_load_to_snowflake,
    user_playlist_items_load_to_snowflake
)

token_response = get_access_token_via_refresh_token(REFRESH_TOKEN)
access_token = token_response["access_token"]

# Recent Tracks


def process_recent_tracks():


    # Extract
    tracks = get_recent_tracks(access_token)

    # save raw API Response and Flatten
    save_json(tracks, "/opt/airflow/spotify/data/recent_tracks.json")
    flatten_recent_tracks()

    # Load into snowflake
    user_recent_tracks_load_to_snowflake()

def process_user_saved_tracks():

    # Extract
    tracks = get_users_saved_tracks(access_token)

    # save raw API Response and Flatten
    save_json(tracks, "/opt/airflow/spotify/data/user_saved_tracks.json")
    flatten_saved_tracks()

    # Load into snowflake
    user_saved_tracks_load_to_snowflake()

def process_user_top_tracks():

    # Extract
    tracks = get_users_top_tracks(access_token,"tracks")

    # save raw API Response and Flatten
    save_json(tracks, "/opt/airflow/spotify/data/user_top_tracks.json")
    flatten_user_top_tracks()

    # Load into snowflake
    user_top_tracks_load_to_snowflake()

def process_user_top_artists():

    # Extract
    tracks = get_users_top_artists(access_token,"artists")

    # save raw API Response and Flatten
    save_json(tracks, "/opt/airflow/spotify/data/user_top_artists.json")
    flatten_user_top_artists()

    # Load into snowflake
    user_top_artist_load_to_snowflake()      

def process_user_playlist_and_items():

    # Extract
    user_playlist_items, user_playlists = get_user_playlists(access_token)

    # save raw API Response and Flatten
    save_json(user_playlists, "/opt/airflow/spotify/data/user_playlist.json")
    save_json(user_playlist_items, "/opt/airflow/spotify/data/user_playlist_tracks.json")
    flatten_user_playlist_items()
    flatten_user_playlist()

    # Load into snowflake
    user_playlist_items_load_to_snowflake()
    user_playlist_load_to_snowflake()
        

# DAG


with DAG(
    dag_id="spotify_api_load_to_snowflake",
    start_date=datetime(2026, 9, 17), 
    schedule=None,
    catchup=False,
    tags=["spotify","api-data-load","snowflake"]
) as dag:
    t1 = PythonOperator(task_id="load_api_data_recent_tracks_snowflake", python_callable=process_recent_tracks)
    t2 = PythonOperator(task_id="load_api_data_saved_tracks_snowflake", python_callable=process_user_saved_tracks)
    t3 = PythonOperator(task_id="load_api_data_user_top_tracks_snowflake", python_callable=process_user_top_tracks)
    t4 = PythonOperator(task_id="load_api_data_user_top_artists_snowflake", python_callable=process_user_top_artists)
    t5 = PythonOperator(task_id="load_api_data_user_playlist_and_items_snowflake", python_callable=process_user_playlist_and_items)

    t1 >> t2 >> t3 >> t4 >> t5
    


