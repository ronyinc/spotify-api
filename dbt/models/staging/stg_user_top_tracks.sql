
select 
        track_id
       ,track_name
       ,type
       ,track_number
       ,duration_ms
       ,artist_name
       ,album_type
       ,album_name
       ,album_release_date
       ,album_total_tracks

       ,loaded_at
       ,loaded_at_year
       ,loaded_at_month

from 
      {{ source('spotify_analytics', 'user_top_tracks') }}       