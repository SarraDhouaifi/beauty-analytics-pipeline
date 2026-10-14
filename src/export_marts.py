"""Export the dbt marts to CSV (dashboard/exports/) for Power BI users who prefer files
over a live PostgreSQL connection."""
import pandas as pd

from config import EXPORTS, get_engine

MARTS = ["dim_products", "fct_reviews", "mart_brand_performance", "mart_category_summary", "mart_monthly_reviews"]


def main() -> None:
    engine = get_engine()
    EXPORTS.mkdir(parents=True, exist_ok=True)
    for table in MARTS:
        df = pd.read_sql(f"SELECT * FROM marts.{table}", engine)
        df.to_csv(EXPORTS / f"{table}.csv", index=False)
        print(f"{table}: {len(df):,} rows")


if __name__ == "__main__":
    main()
