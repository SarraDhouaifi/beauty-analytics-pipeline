-- Category x price band summary: where are the most loved and best rated products?
select
    primary_category,
    secondary_category,
    price_band,
    count(*)                                       as products,
    round(cast(avg(price_usd) as numeric), 2)      as avg_price_usd,
    sum(loves_count)                               as total_loves,
    round(cast(avg(avg_rating) as numeric), 2)     as avg_rating,
    round(cast(avg(avg_sentiment) as numeric), 3)  as avg_sentiment,
    sum(case when is_on_sale then 1 else 0 end)    as products_on_sale
from {{ ref('dim_products') }}
group by primary_category, secondary_category, price_band
