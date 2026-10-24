
with stg_cte as 

(
select   
         playlist_id
        ,playlist_name
        ,playlist_type
        ,playlist_id_owner_name
        ,owner_id
        ,items_href
        ,items_total
        ,row_number() OVER (
            PARTITION BY playlist_id
            ORDER BY loaded_at DESC
        ) AS rnk
        
from 
      {{ ref('stg_user_playlist') }}
)
select 
         playlist_id
        ,playlist_name
        ,playlist_type
        ,playlist_id_owner_name
        ,owner_id
        ,items_href
        ,items_total

from  stg_cte where rnk = 1  