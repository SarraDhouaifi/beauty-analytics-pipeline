# Power BI dashboard – build guide

The dbt marts are designed to be loaded as is. Build time: about 2–3 hours.

## 1. Connect to the data

**Option A – live (recommended):** Home → Get data → PostgreSQL database
- Server: `localhost:5432` – Database: `sephora` – user / password: `sephora` / `sephora`
- Select the tables in the `marts` schema: `dim_products`, `fct_reviews`, `mart_brand_performance`, `mart_category_summary`, `mart_monthly_reviews`

**Option B – files:** Get data → Text/CSV and load the files in `dashboard/exports/` (created by `src/export_marts.py`).

## 2. Data model

- Relationship: `dim_products[product_id]` 1 → * `fct_reviews[product_id]` (single direction)
- Add a date table: Modeling → New table
  ```
  Calendar = CALENDAR(MIN(fct_reviews[review_date]), MAX(fct_reviews[review_date]))
  ```
  then relate `Calendar[Date]` 1 → * `fct_reviews[review_date]` and mark it as a date table.

## 3. DAX measures

```
Reviews = COUNTROWS(fct_reviews)

Avg Rating = AVERAGE(fct_reviews[rating])

Avg Sentiment = AVERAGE(fct_reviews[sentiment_score])

% Negative Reviews =
DIVIDE(CALCULATE([Reviews], fct_reviews[sentiment_label] = "negative"), [Reviews])

Recommendation Rate =
DIVIDE(CALCULATE([Reviews], fct_reviews[is_recommended] = TRUE()), [Reviews])

Total Loves = SUM(dim_products[loves_count])

Avg Price = AVERAGE(dim_products[price_usd])

Reviews MoM % =
VAR Prev = CALCULATE([Reviews], DATEADD('Calendar'[Date], -1, MONTH))
RETURN DIVIDE([Reviews] - Prev, Prev)
```

## 4. Report pages

**Page 1 – Overview**
- KPI cards: Reviews, Avg Rating, Avg Sentiment, % Negative Reviews, Recommendation Rate
- Line chart: Reviews and % Negative Reviews by month
- Slicers: primary category, brand, price band, skin type

**Page 2 – Brands**
- Scatter: Avg Price (x) vs Avg Sentiment (y), size = Total Loves, details = brand
- Table: brand scorecard from `mart_brand_performance`, conditional formatting on % negative

**Page 3 – Categories & pricing**
- Stacked bar: Total Loves by primary category and price band
- Matrix: secondary category × price band, values = Avg Rating

**Page 4 – Customer voice**
- Bar: % Negative Reviews by skin type
- Table: products with the highest sentiment but low popularity ("hidden gems")

## 5. Finish

- One colour per meaning (e.g. blue = volume, orange = negative), consistent across pages
- Titles that state the insight ("Skincare drives most customer love"), not just the metric
- Export a PDF and screenshots into `dashboard/preview/` for the GitHub README
