
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator 
from spotify.auth.token_manager import get_access_token_via_refresh_token
from spotify.utils.file_utils import save_json
from spotify.config import REFRESH_TOKEN 

from spotify.extract.api_end_point_extract import (
    get_recent_tracks,
    get_users_saved_tracks
)

from spotify.extract.flatten_data import (
    flatten_recent_tracks,
    flatten_saved_tracks
)

from spotify.load.snowflake_loader import (
    user_recent_tracks_load_to_snowflake,
    user_saved_tracks_load_to_snowflake,
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

    t1 >> t2


