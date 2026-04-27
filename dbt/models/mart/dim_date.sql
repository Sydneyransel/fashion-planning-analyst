with dates as (
    select distinct week_start from {{ ref('stg_google_trends') }}
),

date_dim as (
    select
        md5(week_start::varchar)      as date_key,
        week_start,
        month(week_start)             as month,
        quarter(week_start)           as quarter,
        year(week_start)              as year,
        case
            when month(week_start) in (12, 1, 2)  then 'Winter'
            when month(week_start) in (3, 4, 5)   then 'Spring'
            when month(week_start) in (6, 7, 8)   then 'Summer'
            when month(week_start) in (9, 10, 11) then 'Fall'
        end as season
    from dates
)

select * from date_dim
