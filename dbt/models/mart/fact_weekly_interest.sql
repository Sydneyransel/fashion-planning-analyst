with stg as (
    select * from {{ ref('stg_google_trends') }}
),

dim_cat as (
    select * from {{ ref('dim_category') }}
),

dim_dt as (
    select * from {{ ref('dim_date') }}
),

fact as (
    select
        md5(stg.keyword || '|' || stg.week_start::varchar) as interest_key,
        dim_cat.category_key,
        dim_dt.date_key,
        stg.interest_score,
        stg.loaded_at
    from stg
    left join dim_cat on stg.keyword = dim_cat.keyword
    left join dim_dt  on stg.week_start = dim_dt.week_start
)

select * from fact
