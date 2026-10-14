-- Product dimension with review-based KPIs, ready for the dashboard
with reviews as (
    select
        product_id,
        count(*)                                                         as reviews_collected,
        avg(sentiment_score)                                             as avg_sentiment,
        avg(case when sentiment_label = 'negative' then 1.0 else 0 end)  as negative_share,
        avg(case when is_recommended then 1.0 else 0 end)                as recommendation_rate
    from {{ ref('stg_reviews') }}
    group by product_id
)

select
    p.*,
    coalesce(r.reviews_collected, 0)                 as reviews_collected,
    round(cast(r.avg_sentiment as numeric), 3)       as avg_sentiment,
    round(cast(r.negative_share as numeric), 3)      as negative_share,
    round(cast(r.recommendation_rate as numeric), 3) as recommendation_rate,
    rank() over (order by p.loves_count desc)        as popularity_rank
from {{ ref('stg_products') }} p
left join reviews r on p.product_id = r.product_id
