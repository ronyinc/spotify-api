select 
      distinct
      artist_id,
      artist_rank,
      artist_name,
      record_type,
      artist_spotify_url,
      loaded_at_year,
      loaded_at_month
from 
      {{ ref('stg_user_top_artists') }}