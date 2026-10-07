
select 
      track_id
     ,track_name
     ,track_type
     ,album_id
     ,album_name
     ,track_number
     ,album_release_date
     ,played_at
     ,album_type
     ,artist_name
     ,loaded_at
from  
      {{ source('spotify_analytics', 'recent_tracks') }}