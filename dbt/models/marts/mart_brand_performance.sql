-- Brand scorecard: catalogue, price positioning, popularity and customer satisfaction
with products as (
    select
        brand_name,
        count(*)                       as products,
        avg(price_usd)                 as avg_price_usd,
        sum(loves_count)               as total_loves,
        avg(avg_rating)                as avg_product_rating
    from {{ ref('stg_products') }}
    group by brand_name
),

reviews as (
    select
        brand_name,
        count(*)                                                         as reviews,
        avg(sentiment_score)                                             as avg_sentiment,
        avg(case when sentiment_label = 'negative' then 1.0 else 0 end)  as negative_share,
        avg(case when is_recommended then 1.0 else 0 end)                as recommendation_rate
    from {{ ref('fct_reviews') }}
    group by brand_name
)

select
    p.brand_name,
    p.products,
    round(cast(p.avg_price_usd as numeric), 2)        as avg_price_usd,
    p.total_loves,
    round(cast(p.avg_product_rating as numeric), 2)   as avg_product_rating,
    coalesce(r.reviews, 0)                            as reviews,
    round(cast(r.avg_sentiment as numeric), 3)        as avg_sentiment,
    round(cast(r.negative_share as numeric), 3)       as negative_share,
    round(cast(r.recommendation_rate as numeric), 3)  as recommendation_rate
from products p
left join reviews r on p.brand_name = r.brand_name
