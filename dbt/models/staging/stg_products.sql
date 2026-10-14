-- One clean row per product: typed columns, effective price and price band
with source as (
    select * from {{ source('raw', 'products') }}
)

select
    product_id,
    product_name,
    brand_name,
    primary_category,
    coalesce(secondary_category, 'Other')                    as secondary_category,
    cast(price_usd as numeric(10, 2))                        as price_usd,
    cast(coalesce(sale_price_usd, price_usd) as numeric(10, 2)) as effective_price_usd,
    sale_price_usd is not null                               as is_on_sale,
    case
        when price_usd < 25  then '1. Under $25'
        when price_usd < 50  then '2. $25-50'
        when price_usd < 100 then '3. $50-100'
        else '4. $100+'
    end                                                      as price_band,
    cast(rating as numeric(4, 2))                            as avg_rating,
    coalesce(reviews, 0)                                     as review_count,
    coalesce(loves_count, 0)                                 as loves_count,
    cast(limited_edition as boolean)                         as is_limited_edition,
    cast(new as boolean)                                     as is_new,
    cast(online_only as boolean)                             as is_online_only,
    cast(out_of_stock as boolean)                            as is_out_of_stock,
    cast(sephora_exclusive as boolean)                       as is_exclusive
from source
where product_id is not null
