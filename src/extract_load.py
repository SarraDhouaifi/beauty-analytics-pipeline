"""Extract the Sephora CSV files, validate them and load them into the raw schema.

Tables created:
    raw.products   one row per product
    raw.reviews    one row per review (review_id added)
"""
import logging

import pandas as pd

from config import DATA, drop_table, get_engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PRODUCT_COLS = ["product_id", "product_name", "brand_id", "brand_name", "loves_count", "rating", "reviews",
                "price_usd", "sale_price_usd", "limited_edition", "new", "online_only", "out_of_stock",
                "sephora_exclusive", "primary_category", "secondary_category"]
REVIEW_COLS = ["author_id", "rating", "is_recommended", "helpfulness", "total_feedback_count",
               "submission_time", "review_text", "review_title", "skin_tone", "skin_type",
               "product_id", "brand_name", "price_usd"]


def validate(df: pd.DataFrame, name: str, required: list[str], key: str | None = None) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{name}: missing columns {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{name}: no rows")
    if key and df[key].duplicated().any():
        raise ValueError(f"{name}: duplicated {key}")
    log.info("%s: %s rows, schema OK", name, f"{len(df):,}")


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    products = pd.read_csv(DATA / "product_info.csv")
    validate(products, "products", PRODUCT_COLS, key="product_id")

    files = sorted(DATA.glob("reviews_*.csv"))
    if not files:
        raise FileNotFoundError(f"No reviews_*.csv file in {DATA}")
    reviews = pd.concat((pd.read_csv(f, usecols=lambda c: c in REVIEW_COLS, low_memory=False) for f in files),
                        ignore_index=True)
    validate(reviews, "reviews", REVIEW_COLS)
    return products[PRODUCT_COLS], reviews[REVIEW_COLS]


def transform(products: pd.DataFrame, reviews: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    reviews = reviews.drop_duplicates()
    reviews = reviews[reviews["product_id"].isin(products["product_id"])]   # orphan reviews
    reviews = reviews.reset_index(drop=True)
    reviews.insert(0, "review_id", reviews.index + 1)
    reviews["author_id"] = reviews["author_id"].astype(str)
    return products, reviews


def load(products: pd.DataFrame, reviews: pd.DataFrame) -> None:
    engine = get_engine()
    drop_table(engine, "raw.products")
    drop_table(engine, "raw.reviews")
    products.to_sql("products", engine, schema="raw", if_exists="replace", index=False)
    reviews.to_sql("reviews", engine, schema="raw", if_exists="replace", index=False, chunksize=50_000)
    log.info("Loaded raw.products (%s) and raw.reviews (%s)", f"{len(products):,}", f"{len(reviews):,}")


def main() -> None:
    load(*transform(*extract()))


if __name__ == "__main__":
    main()
