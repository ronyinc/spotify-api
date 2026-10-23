
select   distinct
         playlist_id
        ,playlist_name
        ,playlist_type
        ,playlist_id_owner_name
        ,owner_id
        ,items_href
        ,items_total
        

from 
      {{ ref('stg_user_playlist') }}        