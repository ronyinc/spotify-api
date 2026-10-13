
select 
         playlist_item_key
        ,added_at
        ,item_id
        ,item_name
        ,playlist_id
        ,playlist_added_by_user_id
        ,item_album_type
        ,item_album_href
        ,item_album_id
        ,item_album_name
        ,item_album_release_date
        ,item_duration_ms
        ,loaded_at

from 
     {{ source('spotify_analytics', 'user_playlist_items') }}       


