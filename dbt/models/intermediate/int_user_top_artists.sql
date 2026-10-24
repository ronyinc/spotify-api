
with stg_cte as 
(
      select 
            artist_id,
            artist_rank,
            artist_name,
            record_type,
            artist_spotify_url,
            loaded_at_year,
            loaded_at_month,
            row_number() OVER (
            PARTITION BY artist_id,loaded_at_year,loaded_at_month
            ORDER BY loaded_at DESC
        ) AS rnk
      from 
            {{ ref('stg_user_top_artists') }}
)

select 
      artist_id,
      CAST(artist_rank AS NUMBER(38,0)) AS artist_rank,
      artist_name,
      record_type,
      artist_spotify_url,
      loaded_at_year,
      loaded_at_month
from 
      stg_cte
where rnk = 1      
     
