
select
        playlist_id
        ,name as playlist_name
        ,type as playlist_type
        ,playlist_id_owner_name
        ,owner_id
        ,items_href
        ,items_total
        ,loaded_at
from   
     {{ source('spotify_analytics', 'user_playlist') }}