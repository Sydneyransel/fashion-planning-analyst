with keywords as (
    select distinct keyword from {{ ref('stg_google_trends') }}
),

categorized as (
    select
        md5(keyword)  as category_key,
        keyword,
        case keyword
            when 'shapewear'  then 'intimates'
            when 'bodysuit'   then 'intimates'
            when 'bra'        then 'intimates'
            when 'underwear'  then 'intimates'
            when 'skims'      then 'brand'
            when 'dress'      then 'ready-to-wear'
            when 'loungewear' then 'lounge'
            when 'pajamas'    then 'lounge'
            when 'swim'       then 'swim'
            else 'other'
        end as category_group
    from keywords
)

select * from categorized
