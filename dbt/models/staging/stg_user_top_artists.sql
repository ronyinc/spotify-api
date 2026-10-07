
select 
      artist_id,
      artist_name,
      type as record_type,
      artist_spotify_url,
      loaded_at,
      loaded_at_year,
      loaded_at_month
      
from {{ source('spotify_analytics', 'user_top_artists')}}      