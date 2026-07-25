with source as (

    select * from {{ source('raw', 'example_events') }}

),

renamed as (

    select
        id as event_id,
        occurred_at

    from source

)

select * from renamed
