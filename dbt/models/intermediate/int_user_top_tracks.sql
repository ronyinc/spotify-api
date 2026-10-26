
with stg_cte as 

(
  select 
        track_id
       ,track_name
       ,track_rank
       ,type
       ,track_number
       ,duration_ms
       ,artist_name
       ,album_type
       ,album_name
       ,album_release_date
       ,album_total_tracks
       ,loaded_at_year
       ,loaded_at_month

       ,row_number() OVER (
            PARTITION BY track_id,loaded_at_year,loaded_at_month
            ORDER BY loaded_at DESC
        ) AS rnk

  from  
       {{ ref('stg_user_top_tracks') }}

)

select 
       track_id
       ,track_name
       ,cast(track_rank as NUMBER(38,0)) as track_rank
       ,type
       ,track_number
       ,duration_ms
       ,artist_name
       ,album_type
       ,album_name
       ,album_release_date
       ,album_total_tracks
       ,loaded_at_year
       ,loaded_at_month
from 
      stg_cte 
where rnk = 1           