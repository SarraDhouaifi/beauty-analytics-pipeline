-- Review fact table (grain: one review), joined to product attributes used for filtering
select
    r.review_id,
    r.product_id,
    p.brand_name,
    p.primary_category,
    p.price_band,
    r.review_date,
    cast(date_trunc('month', r.review_date) as date) as review_month,
    r.rating,
    r.is_recommended,
    r.sentiment_score,
    r.sentiment_label,
    r.skin_type,
    r.skin_tone
from {{ ref('stg_reviews') }} r
join {{ ref('stg_products') }} p on r.product_id = p.product_id
