"""Generate synthetic files with the same schema as the Kaggle
"Sephora Products and Skincare Reviews" dataset (only the columns used here).

Creates data/product_info.csv and data/reviews_0-250.csv. Use it only for testing.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(11)
DATA = Path(__file__).resolve().parents[1] / "data"

BRANDS = ["Lumiere", "Verdance", "Nocturne", "Aurelle", "Kaya", "Belle Rive", "Solenne", "Mirai"]
CATEGORIES = {
    "Skincare": ["Moisturizers", "Cleansers", "Treatments", "Eye Care"],
    "Makeup": ["Face", "Eye", "Lip"],
    "Hair": ["Shampoo & Conditioner", "Treatments"],
    "Fragrance": ["Women", "Men"],
}
POSITIVE = ["I love this product, my skin feels amazing.", "Great texture and smells wonderful.",
            "Best purchase this year, highly recommend!", "Works really well, I will buy again."]
NEGATIVE = ["Broke me out, very disappointed.", "Terrible smell and it dried my skin.",
            "Not worth the price, did nothing for me.", "Awful, it irritated my face."]
NEUTRAL = ["It is okay, nothing special.", "Average product, does the job."]


def main(n_products: int = 400, n_reviews: int = 20000) -> None:
    rows = []
    for i in range(n_products):
        primary = RNG.choice(list(CATEGORIES))
        price = round(float(RNG.lognormal(3.4, 0.6)), 2)
        rows.append({
            "product_id": f"P{100000 + i}",
            "product_name": f"Product {i}",
            "brand_id": int(RNG.integers(1, len(BRANDS) + 1)),
            "brand_name": RNG.choice(BRANDS),
            "loves_count": int(RNG.lognormal(8, 1.5)),
            "rating": round(float(RNG.uniform(3, 5)), 4),
            "reviews": int(RNG.integers(0, 2000)),
            "price_usd": price,
            "sale_price_usd": round(price * 0.8, 2) if RNG.random() < 0.1 else np.nan,
            "limited_edition": int(RNG.random() < 0.08),
            "new": int(RNG.random() < 0.1),
            "online_only": int(RNG.random() < 0.2),
            "out_of_stock": int(RNG.random() < 0.05),
            "sephora_exclusive": int(RNG.random() < 0.25),
            "primary_category": primary,
            "secondary_category": RNG.choice(CATEGORIES[primary]),
        })
    products = pd.DataFrame(rows)

    p = products.sample(n_reviews, replace=True, random_state=1).reset_index(drop=True)
    rating = RNG.choice([1, 2, 3, 4, 5], n_reviews, p=[0.06, 0.06, 0.1, 0.2, 0.58])
    text = [RNG.choice(POSITIVE if r >= 4 else NEGATIVE if r <= 2 else NEUTRAL) for r in rating]
    dates = pd.to_datetime("2019-01-01") + pd.to_timedelta(RNG.integers(0, 4 * 365, n_reviews), unit="D")
    reviews = pd.DataFrame({
        "author_id": RNG.integers(1_000_000, 9_999_999, n_reviews).astype(str),
        "rating": rating,
        "is_recommended": np.where(rating >= 4, 1.0, np.where(rating <= 2, 0.0, np.nan)),
        "helpfulness": RNG.uniform(0, 1, n_reviews).round(3),
        "total_feedback_count": RNG.integers(0, 30, n_reviews),
        "submission_time": dates.strftime("%Y-%m-%d"),
        "review_text": text,
        "review_title": "Review",
        "skin_tone": RNG.choice(["light", "medium", "tan", "deep", None], n_reviews),
        "skin_type": RNG.choice(["dry", "oily", "combination", "normal", None], n_reviews),
        "product_id": p["product_id"],
        "product_name": p["product_name"],
        "brand_name": p["brand_name"],
        "price_usd": p["price_usd"],
    })

    DATA.mkdir(exist_ok=True)
    products.to_csv(DATA / "product_info.csv", index=False)
    reviews.to_csv(DATA / "reviews_0-250.csv")   # the real files also start with an unnamed index column
    print(f"Wrote {len(products)} products and {len(reviews):,} reviews to {DATA}")


if __name__ == "__main__":
    main()
