with source as (
    select * from {{ source('raw', 'GOOGLE_TRENDS_WEEKLY') }}
)

select
    keyword,
    week_start::date    as week_start,
    interest_score::int as interest_score,
    loaded_at
from source
