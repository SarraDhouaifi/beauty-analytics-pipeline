-- Monthly trend of review volume, rating and sentiment by category
select
    review_month,
    primary_category,
    count(*)                                                                  as reviews,
    round(cast(avg(rating) as numeric), 2)                                    as avg_rating,
    round(cast(avg(sentiment_score) as numeric), 3)                           as avg_sentiment,
    round(cast(avg(case when sentiment_label = 'negative' then 1.0 else 0 end) as numeric), 3) as negative_share
from {{ ref('fct_reviews') }}
group by review_month, primary_category
