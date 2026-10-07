
select 
        track_id
        ,track_name
        ,track_duration_ms
        ,track_album_id
        ,track_album_name
        ,added_at
        ,track_album_type
        ,artist_name
        ,track_album_href
        ,track_album_release_date
        ,track_spotify_url
        ,loaded_at

from 
        {{ source('spotify_analytics', 'saved_tracks') }}      