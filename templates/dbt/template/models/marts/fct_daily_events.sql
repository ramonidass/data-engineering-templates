with events as (

    select * from {{ ref('stg_example_events') }}

)

select
    cast(occurred_at as date) as event_date,
    count(*) as event_count

from events
group by 1
