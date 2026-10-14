-- One clean row per review, enriched with its sentiment score
with reviews as (
    select * from {{ source('raw', 'reviews') }}
),

sentiment as (
    select * from {{ source('raw', 'review_sentiment') }}
)

select
    r.review_id,
    r.product_id,
    r.author_id,
    cast(r.submission_time as date)                          as review_date,
    cast(r.rating as integer)                                as rating,
    case when r.is_recommended = 1 then true
         when r.is_recommended = 0 then false end            as is_recommended,
    coalesce(r.total_feedback_count, 0)                      as feedback_count,
    lower(coalesce(r.skin_type, 'unknown'))                  as skin_type,
    lower(coalesce(r.skin_tone, 'unknown'))                  as skin_tone,
    s.sentiment_score,
    s.sentiment_label
from reviews r
left join sentiment s on r.review_id = s.review_id
where r.rating between 1 and 5
