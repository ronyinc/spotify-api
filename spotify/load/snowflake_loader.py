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
        conn.commit()

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

        conn.commit()

    finally:
        cursor.close()
        conn.close() 


# load only new or updated records into the RAW layer. Then stage _dedupe to clean
# intermediate layer > normalize if required. 

def user_playlist_items_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/user_playlist_items.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    
    try:
        
        cursor.execute("""
                CREATE TEMPORARY TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS_TMP (
                       PLAYLIST_ITEM_KEY VARCHAR,
                       ADDED_AT TIMESTAMP_TZ,
                       ITEM_ID VARCHAR,
                       ITEM_NAME VARCHAR,
                       PLAYLIST_ID VARCHAR,
                       PLAYLIST_ADDED_BY_USER_ID VARCHAR,
                       ITEM_ALBUM_TYPE VARCHAR,
                       ITEM_ALBUM_HREF VARCHAR,
                       ITEM_ALBUM_ID VARCHAR,
                       ITEM_ALBUM_NAME VARCHAR,
                       ITEM_ALBUM_RELEASE_DATE DATE,
                       ITEM_DURATION_MS NUMERIC,
                       LOADED_AT TIMESTAMP_TZ
                )
            """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "USER_PLAYLIST_ITEMS_TMP",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=True
        )
        
        print(f"Successfully loaded {num_rows} into the tmp table - RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS_TMP ")
        print("\n")

        insert_sql = f"""
        INSERT INTO RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS (
        PLAYLIST_ITEM_KEY, ADDED_AT, ITEM_ID, ITEM_NAME, PLAYLIST_ID, PLAYLIST_ADDED_BY_USER_ID, ITEM_ALBUM_TYPE, ITEM_ALBUM_HREF,
        ITEM_ALBUM_ID, ITEM_ALBUM_NAME, ITEM_ALBUM_RELEASE_DATE, ITEM_DURATION_MS, LOADED_AT
         )
         SELECT
                tmp.PLAYLIST_ITEM_KEY, tmp.ADDED_AT, tmp.ITEM_ID, tmp.ITEM_NAME, tmp.PLAYLIST_ID, tmp.PLAYLIST_ADDED_BY_USER_ID, tmp.ITEM_ALBUM_TYPE, tmp.ITEM_ALBUM_HREF,
                tmp.ITEM_ALBUM_ID, tmp.ITEM_ALBUM_NAME, tmp.ITEM_ALBUM_RELEASE_DATE, tmp.ITEM_DURATION_MS, tmp.LOADED_AT
         FROM 
                 RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS_TMP tmp
         LEFT JOIN 
                    RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS trg
         ON tmp.PLAYLIST_ITEM_KEY = trg.PLAYLIST_ITEM_KEY
         WHERE trg.PLAYLIST_ITEM_KEY IS NULL and tmp.ITEM_ID is not NULL;           
        """
        cursor.execute(insert_sql)
        print(f"Inserted {cursor.rowcount} rows")

        update_sql = f"""
        UPDATE RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS as trg
        SET
            ADDED_AT = tmp.ADDED_AT,
            ITEM_NAME = tmp.ITEM_NAME,
            PLAYLIST_ID = tmp.PLAYLIST_ID,
            PLAYLIST_ADDED_BY_USER_ID = tmp.PLAYLIST_ADDED_BY_USER_ID,
            ITEM_ALBUM_TYPE = tmp.ITEM_ALBUM_TYPE,
            ITEM_ALBUM_HREF = tmp.ITEM_ALBUM_HREF,
            ITEM_ALBUM_ID = tmp.ITEM_ALBUM_ID,
            ITEM_ALBUM_NAME = tmp.ITEM_ALBUM_NAME,
            ITEM_ALBUM_RELEASE_DATE = tmp.ITEM_ALBUM_RELEASE_DATE,
            ITEM_DURATION_MS = tmp.ITEM_DURATION_MS, 
            LOADED_AT = tmp.LOADED_AT
        FROM 
             RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_ITEMS_TMP tmp
        WHERE trg.PLAYLIST_ITEM_KEY = tmp.PLAYLIST_ITEM_KEY
        AND (
               trg.ADDED_AT IS DISTINCT FROM tmp.ADDED_AT OR 
               trg.ITEM_ID IS DISTINCT FROM tmp.ITEM_ID OR
               trg.ITEM_NAME IS DISTINCT FROM tmp.ITEM_NAME OR
               trg.PLAYLIST_ID IS DISTINCT FROM tmp.PLAYLIST_ID OR
               trg.PLAYLIST_ADDED_BY_USER_ID IS DISTINCT FROM tmp.PLAYLIST_ADDED_BY_USER_ID OR
               trg.ITEM_ALBUM_TYPE IS DISTINCT FROM tmp.ITEM_ALBUM_TYPE OR 
               trg.ITEM_ALBUM_HREF IS DISTINCT FROM tmp.ITEM_ALBUM_HREF OR 
               trg.ITEM_ALBUM_ID IS DISTINCT FROM tmp.ITEM_ALBUM_ID OR
               trg.ITEM_ALBUM_NAME IS DISTINCT FROM tmp.ITEM_ALBUM_NAME OR 
               trg.ITEM_ALBUM_RELEASE_DATE IS DISTINCT FROM tmp.ITEM_ALBUM_RELEASE_DATE OR
               trg.ITEM_DURATION_MS IS DISTINCT FROM tmp.ITEM_DURATION_MS  
        )        
        """
        cursor.execute(update_sql)
        print(f"Updated {cursor.rowcount} changed rows")
        conn.commit()

    finally:
        cursor.close()
        conn.close() 


# load user playlists.... append all in RAW, stage --> Dedupe . 
# intermediate --> mereg new records and update existing if any.  

def user_playlist_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/user_playlist.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    
    try:
        
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.USER_PLAYLIST (
                       PLAYLIST_ID VARCHAR,
                       NAME VARCHAR,
                       TYPE VARCHAR,
                       PLAYLIST_ID_OWNER_NAME VARCHAR,
                       OWNER_ID VARCHAR,
                       ITEMS_HREF VARCHAR,
                       ITEMS_TOTAL NUMERIC,
                       LOADED_AT TIMESTAMP_TZ
                )
            """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "USER_PLAYLIST",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=False
        )
        
        print(f"Successfully loaded {num_rows} into the table - RAW.SPOTIFY_SCHEMA.USER_PLAYLIST ")
        print("\n")

        conn.commit()

    finally:
        cursor.close()
        conn.close()

# load user top artists... append all in RAW, stage --> Dedupe . 
# intermediate --> mereg new records and update existing if any.



def user_top_artist_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/user_top_artists.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)
    df["loaded_at_year"] = df["loaded_at"].dt.year
    df["loaded_at_month"] = df["loaded_at"].dt.month

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    try:
        
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.USER_TOP_ARTISTS (
                       ARTIST_ID VARCHAR,
                       ARTIST_NAME VARCHAR,
                       TYPE VARCHAR,
                       ARTIST_SPOTIFY_URL VARCHAR,
                       LOADED_AT TIMESTAMP_TZ,
                       LOADED_AT_YEAR NUMBER(4,0),
                       LOADED_AT_MONTH NUMBER(4,0)
                )
            """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "USER_TOP_ARTISTS",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=False,
            use_logical_type=True
        )
        
        print(f"Successfully loaded {num_rows} into the table - RAW.SPOTIFY_SCHEMA.USER_TOP_ARTISTS")
        print("\n")

        conn.commit()

    finally:
        cursor.close()
        conn.close()

# load only new or updated records into the RAW layer. Then stage _dedupe to clean
# intermediate layer > normalize if required. 

def user_top_tracks_load_to_snowflake():

    csv_path = "/opt/airflow/spotify/data/user_top_tracks.csv"

    df = pd.read_csv(csv_path)
    df["loaded_at"] = datetime.now(timezone.utc)
    df["loaded_at_year"] = df["loaded_at"].dt.year
    df["loaded_at_month"] = df["loaded_at"].dt.month

    df.columns = df.columns.str.upper()

    print(f"Loaded CSV with {len(df)} rows")

    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    try:
        
        cursor.execute("""
                CREATE TEMPORARY TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS_TMP (
                       TRACK_ID VARCHAR,
                       TRACK_NAME VARCHAR,
                       TYPE VARCHAR,
                       TRACK_NUMBER VARCHAR,
                       DURATION_MS NUMERIC,
                       ARTIST_NAME VARCHAR,
                       ALBUM_TYPE VARCHAR,
                       ALBUM_NAME VARCHAR,
                       ALBUM_RELEASE_DATE VARCHAR,
                       ALBUM_TOTAL_TRACKS NUMERIC,
                       LOADED_AT TIMESTAMP_TZ,
                       LOADED_AT_YEAR NUMBER(4,0),
                       LOADED_AT_MONTH NUMBER(4,0)
                )
            """)

        success, num_chunks, num_rows, _ =  write_pandas(
            conn, 
            df,
            table_name = "USER_TOP_TRACKS_TMP",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=True,
            use_logical_type=True
        )
        
        print(f"Successfully loaded {num_rows} into the tmp table - RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS_TMP ")
        print("\n")


        insert_sql = f"""
        INSERT INTO RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS (
                TRACK_ID, TRACK_NAME, TYPE, TRACK_NUMBER, DURATION_MS, ARTIST_NAME, ALBUM_TYPE, ALBUM_NAME, ALBUM_RELEASE_DATE, ALBUM_TOTAL_TRACKS, 
                LOADED_AT, LOADED_AT_YEAR, LOADED_AT_MONTH  
         )
         SELECT
                tmp.TRACK_ID, tmp.TRACK_NAME, tmp.TYPE, tmp.TRACK_NUMBER, tmp.DURATION_MS, tmp.ARTIST_NAME, tmp.ALBUM_TYPE, tmp.ALBUM_NAME, 
                tmp.ALBUM_RELEASE_DATE, tmp.ALBUM_TOTAL_TRACKS, tmp.LOADED_AT, tmp.LOADED_AT_YEAR, tmp.LOADED_AT_MONTH
         FROM 
                 RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS_TMP tmp
         LEFT JOIN 
                    RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS trg
         ON tmp.TRACK_ID = trg.TRACK_ID
         WHERE trg.TRACK_ID IS NULL;           
        """
        cursor.execute(insert_sql)
        print(f"Inserted {cursor.rowcount} rows")

        update_sql = f"""
        UPDATE RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS as trg
        SET
            TRACK_NAME = tmp.TRACK_NAME,
            TYPE = tmp.TYPE,
            TRACK_NUMBER = tmp.TRACK_NUMBER,
            DURATION_MS = tmp.DURATION_MS,
            ARTIST_NAME = tmp.ARTIST_NAME,
            ALBUM_TYPE = tmp.ALBUM_TYPE,
            ALBUM_NAME = tmp.ALBUM_NAME,
            ALBUM_RELEASE_DATE = tmp.ALBUM_RELEASE_DATE,
            ALBUM_TOTAL_TRACKS = tmp.ALBUM_TOTAL_TRACKS,
            LOADED_AT = tmp.LOADED_AT,
            LOADED_AT_YEAR = tmp.LOADED_AT_YEAR,
            LOADED_AT_MONTH = tmp.LOADED_AT_MONTH
        FROM 
             RAW.SPOTIFY_SCHEMA.USER_TOP_TRACKS_TMP tmp
        WHERE trg.TRACK_ID = tmp.TRACK_ID
        AND (
               trg.TRACK_NAME IS DISTINCT FROM tmp.TRACK_NAME OR
               trg.TYPE IS DISTINCT FROM tmp.TYPE OR
               trg.TRACK_NUMBER IS DISTINCT FROM tmp.TRACK_NUMBER OR
               trg.DURATION_MS IS DISTINCT FROM tmp.DURATION_MS OR
               trg.ARTIST_NAME IS DISTINCT FROM tmp.ARTIST_NAME OR
               trg.ALBUM_TYPE IS DISTINCT FROM tmp.ALBUM_TYPE OR
               trg.ALBUM_NAME IS DISTINCT FROM tmp.ALBUM_NAME OR
               trg.ALBUM_RELEASE_DATE IS DISTINCT FROM tmp.ALBUM_RELEASE_DATE OR
               trg.ALBUM_TOTAL_TRACKS IS DISTINCT FROM tmp.ALBUM_TOTAL_TRACKS
        )        
        """
        cursor.execute(update_sql)
        print(f"Updated {cursor.rowcount} changed rows")

        conn.commit()

    finally:
        cursor.close()
        conn.close()        