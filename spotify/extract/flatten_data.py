import pandas as pd
import json

def flatten_recent_tracks():

    try:

        with open("/opt/airflow/spotify/data/recent_tracks.json","r") as f:
            data = json.load(f)

        # print(data.keys())
        # print('\n')
        # print(type(data["items"]))
        # print('\n')


        df = pd.json_normalize(data)
        # print(df.columns.tolist())

        df['artist_name'] = df["track.artists"].apply(lambda x : ",".join(a['name'] for a in x))

        df_selected = df[["track.id","track.name","track.type","track.album.id","track.album.name",
                        "track.track_number","track.album.release_date","played_at","track.album.type"
                        ,"artist_name"]].rename(columns={"track.album.id":"album_id","track.album.name":"album_name"
                                                        ,"track.album.release_date":"album_release_date","track.album.type":"album_type"
                                                        ,"track.id":"track_id","track.name":"track_name","track.type":"track_type",
                                                        "track.track_number":"track_number" })

        df_selected.to_csv("/opt/airflow/spotify/data/recent_tracks.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Inpput file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e          


def flatten_saved_tracks():

    try:

        with open("/opt/airflow/spotify/data/user_saved_tracks.json","r") as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        print("\n")
        print(df.columns.tolist())

        df['artist_name'] = df["track.artists"].apply(lambda x : ','.join(a["name"] for a in x))

        df['track_spotify_url'] = df["track.artists"].apply(lambda x : ','.join(a["external_urls"]["spotify"] for a in x))

        # logic to generate multiple rows per artist using list comprehension and data frame explode.
        # df['track_spotify_url'] = df["track.artists"].apply(lambda x : [a["external_urls"]["spotify"] for a in x])
        # df = df.explode('track_spotify_url').reset_index(drop=True)


        df_selected = df[["track.id","track.name","track.duration_ms","track.album.id","track.album.name",
                        "added_at","track.album.album_type","artist_name","track.album.href",
                        "track.album.release_date","track_spotify_url"]].rename(columns= {"track.id":"track_id", "track.name":"track_name",
                        "track.duration_ms":"track_duration_ms", "track.album.id":"track_album_id", "track.album.name":"track_album_name", 
                        "track.album.album_type":"track_album_type", "track.album.href":"track_album_href", "track.album.release_date":"track_album_release_date"})

        df_selected.to_csv("/opt/airflow/spotify/data/saved_tracks.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Inpput file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e


def flatten_user_top_artists():

    try:

        with open("/opt/airflow/spotify/data/user_top_artists.json","r") as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        print("\n")
        print(df.columns.tolist())

        df_selected = df[["id","name","type","external_urls.spotify"]].rename(columns={"id":"artist_id","name":"artist_name","external_urls.spotify":"artist_spotify_url"})

        df_selected.to_csv("/opt/airflow/spotify/data/user_top_artists.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Inpput file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e    


def flatten_user_top_tracks():

    try:

        with open("/opt/airflow/spotify/data/user_top_tracks.json","r") as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        df['artist_name'] = df["album.artists"].apply(lambda x : ",".join(a["name"] for a in x))

        print("\n")
        print(df.columns.tolist())

        df_selected = df[["id","name","type","track_number","duration_ms","artist_name","album.album_type",
        "album.name","album.release_date","album.total_tracks"]].rename(columns={"id":"track_id",
        "name":"track_name"})

        df_selected.to_csv("/opt/airflow/spotify/data/user_top_tracks.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Input file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e     


def flatten_user_playlist_items():

    try:

        with open("/opt/airflow/spotify/data/user_playlist_tracks.json","r") as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        print("\n")
        print(df.columns.tolist())

        df['artist_name'] = df["item.artists"].apply(
                                           lambda x : ",".join(a["name"] for a in x)
                                           if isinstance(x, list)
                                           else None
                                           )

        # print(df[df["item.artists"].isna()][["item.name","item.type","item.is_local"]])

        df_selected = df[["added_at","item.id","item.name","playlist_id","added_by.id","item.album.type","item.album.href",
        "item.album.id","item.album.name","item.album.release_date","item.duration_ms"]].rename(columns={"added_by.id":"playlist_added_by_user_id"})

        df_selected.to_csv("/opt/airflow/spotify/data/user_playlist_items.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Input file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e     



def flatten_user_playlist():

    try:

        with open("/opt/airflow/spotify/data/user_playlist.json","r") as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        print("\n")
        print(df.columns.tolist())


        # print(df[df["item.artists"].isna()][["item.name","item.type","item.is_local"]])

        df_selected = df[["id","name","type","owner.display_name","owner.id","items.href",
        "items.total"]].rename(columns={"id":"playlist_id",
        "owner.display_name":"playlist_id_owner_name"})

        df_selected.to_csv("/opt/airflow/spotify/data/user_playlist.csv", index=False, encoding="utf-8")

    except FileNotFoundError as e:
        print("Input file not found")
        raise e

    except json.JSONDecodeError as e:
        print("File exists. But containes corrupt json")
        raise e

    except KeyError as e:
        print("Key/column value missing from the API response. ")
        raise e     

