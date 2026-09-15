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


# load only new or updated records into the RAW layer. Then stage _dedupe
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

    finally:
        cursor.close()
        conn.close() 



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
                CREATE TEMPORARY TABLE IF NOT EXISTS RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_TMP (
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
            table_name = "USER_PLAYLIST_TMP",
            schema = "SPOTIFY_SCHEMA",
            database = "RAW", 
            overwrite=True
        )
        
        print(f"Successfully loaded {num_rows} into the tmp table - RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_TMP ")
        print("\n")

        insert_sql = f"""
        INSERT INTO RAW.SPOTIFY_SCHEMA.USER_PLAYLIST (
                PLAYLIST_ID, NAME, TYPE, PLAYLIST_ID_OWNER_NAME, OWNER_ID, ITEMS_HREF, ITEMS_TOTAL, LOADED_AT
         )
         SELECT
                tmp.PLAYLIST_ID, tmp.NAME, tmp.TYPE, tmp.PLAYLIST_ID_OWNER_NAME, tmp.OWNER_ID, tmp.ITEMS_HREF, tmp.ITEMS_TOTAL, tmp.LOADED_AT
         FROM 
                 RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_TMP tmp
         LEFT JOIN 
                    RAW.SPOTIFY_SCHEMA.USER_PLAYLIST trg
         ON tmp.PLAYLIST_ID = trg.PLAYLIST_ID
         WHERE trg.PLAYLIST_ID IS NULL;           
        """
        cursor.execute(insert_sql)
        print(f"Inserted {cursor.rowcount} rows")

        update_sql = f"""
        UPDATE RAW.SPOTIFY_SCHEMA.USER_PLAYLIST as trg
        SET
            PLAYLIST_ID = tmp.PLAYLIST_ID,
            NAME = tmp.NAME,
            TYPE = tmp.TYPE,
            PLAYLIST_ID_OWNER_NAME = tmp.PLAYLIST_ID_OWNER_NAME,
            OWNER_ID = tmp.OWNER_ID,
            ITEMS_HREF = tmp.ITEMS_HREF,
            ITEMS_TOTAL = tmp.ITEMS_TOTAL,
            LOADED_AT = tmp.LOADED_AT
        FROM 
             RAW.SPOTIFY_SCHEMA.USER_PLAYLIST_TMP tmp
        WHERE trg.PLAYLIST_ID = tmp.PLAYLIST_ID
        AND (
               trg.PLAYLIST_ID IS DISTINCT FROM tmp.PLAYLIST_ID OR 
               trg.NAME IS DISTINCT FROM tmp.NAME OR
               trg.TYPE IS DISTINCT FROM tmp.TYPE OR
               trg.PLAYLIST_ID_OWNER_NAME IS DISTINCT FROM tmp.PLAYLIST_ID_OWNER_NAME OR
               trg.OWNER_ID IS DISTINCT FROM tmp.OWNER_ID OR
               trg.ITEMS_HREF IS DISTINCT FROM tmp.ITEMS_HREF OR 
               trg.ITEMS_TOTAL IS DISTINCT FROM tmp.ITEMS_TOTAL OR 
               trg.LOADED_AT IS DISTINCT FROM tmp.LOADED_AT
        )        
        """
        cursor.execute(update_sql)
        print(f"Updated {cursor.rowcount} changed rows")

    finally:
        cursor.close()
        conn.close()

