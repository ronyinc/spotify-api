{{
    config(
        materialized='incremental',
        unique_key='playlist_item_key',
        incremental_strategy='merge'
    )
}}

select   distinct 
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
     {{ ref('stg_user_playlist_items') }}

{% if is_incremental() %}

where loaded_at >= (
    select DATEADD(day, -1, MAX(loaded_at)) from {{ this }}
)


{% endif %}