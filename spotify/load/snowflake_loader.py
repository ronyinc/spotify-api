import os
import snowflake.connector
import pandas as pd 
from snowflake.connector.pandas_tools import write_pandas
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization

def get_snowflake_connection():
    private_key_path = os.getenv("DBT_PRIVATE_KEY_PATH")

    with open(private_key_path, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,   # unencrypted key — header confirms no passphrase
        )

    private_key_der = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    conn = snowflake.connector.connect(
        account=os.getenv("DBT_SNOWFLAKE_ACCOUNT"),
        user=os.getenv("DBT_SNOWFLAKE_USER"),
        private_key=private_key_der,
        role=os.getenv("DBT_SNOWFLAKE_ROLE"),
        warehouse=os.getenv("DBT_SNOWFLAKE_WAREHOUSE"),
        database="RAW",
        schema="SPOTIFY_SCHEMA"
    )

    return conn


# load user recent tracks. append all in RAW, stage --> Dedupe . 
# intermediate --> mereg new records and update existing if any.  


def user_recent_tracks_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/recent_tracks.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.RECENT_TRACKS (
                TRACK_ID VARCHAR,
                TRACK_NAME VARCHAR,
                TRACK_TYPE VARCHAR,
                ALBUM_ID VARCHAR,
                ALBUM_NAME VARCHAR,
                TRACK_NUMBER NUMBER,
                ALBUM_RELEASE_DATE VARCHAR,
                PLAYED_AT TIMESTAMP_TZ,
                ALBUM_TYPE VARCHAR,
                ARTIST_NAME VARCHAR,
                LOADED_AT TIMESTAMP_TZ
            )
        """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "RECENT_TRACKS",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=False
        )

        print(f"Load Success: {success}")
        print(f"Rows Loaded:  {num_rows}")
        print("\n")
        print("Successfully loaded all the data into the table - RAW.SPOTIFY_SCHEMA.RECENT_TRACKS ")
        print("\n")

    finally:
        cursor.close()
        conn.close() 


# load user saved tracks. append all in RAW, stage --> Dedupe . 
# intermediate --> mereg new records and update existing if any.  


def user_saved_tracks_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/saved_tracks.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.SAVED_TRACKS (
                TRACK_ID VARCHAR,
                TRACK_NAME VARCHAR,
                TRACK_DURATION_MS VARCHAR,
                TRACK_ALBUM_ID VARCHAR,
                TRACK_ALBUM_NAME VARCHAR,
                ADDED_AT TIMESTAMP_TZ,
                TRACK_ALBUM_TYPE VARCHAR,
                ARTIST_NAME VARCHAR,
                TRACK_ALBUM_HREF VARCHAR,
                TRACK_ALBUM_RELEASE_DATE DATE,
                TRACK_SPOTIFY_URL VARCHAR,
                LOADED_AT TIMESTAMP_TZ
            )
        """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "SAVED_TRACKS",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=False
        )

        print(f"Load Success: {success}")
        print(f"Rows Loaded:  {num_rows}")
        print("\n")
        print("Successfully loaded all the data into the table - RAW.SPOTIFY_SCHEMA.SAVED_TRACKS ")

    finally:
        cursor.close()
        conn.close() 

