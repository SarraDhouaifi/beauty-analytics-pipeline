"""Build a static preview of the dashboard (PNG charts + insights.md) from the dbt marts.

The interactive version is built in Power BI (see dashboard/POWERBI_GUIDE.md);
this preview gives the README visuals and computed insights without Power BI.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import ROOT, get_engine

FIG = ROOT / "dashboard" / "preview"
BLUE, ORANGE, GREY = "#2f5d8a", "#c4572a", "#9db4cf"


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    engine = get_engine()
    brands = pd.read_sql("SELECT * FROM marts.mart_brand_performance", engine)
    cats = pd.read_sql("SELECT * FROM marts.mart_category_summary", engine)
    monthly = pd.read_sql("SELECT * FROM marts.mart_monthly_reviews", engine, parse_dates=["review_month"])
    products = pd.read_sql("SELECT * FROM marts.dim_products", engine)
    for df in (brands, cats, monthly, products):          # numeric(…) columns arrive as Decimal
        for c in df.columns:
            if df[c].dtype == object:
                try:
                    df[c] = pd.to_numeric(df[c])
                except (ValueError, TypeError):
                    pass

    # 1. Brand positioning: price vs satisfaction, bubble = popularity
    top = brands.nlargest(15, "total_loves")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(top["avg_price_usd"], top["avg_sentiment"], s=top["total_loves"] / top["total_loves"].max() * 1500,
               color=BLUE, alpha=0.45, edgecolor="white")
    for _, r in top.iterrows():
        ax.annotate(r["brand_name"], (r["avg_price_usd"], r["avg_sentiment"]), fontsize=8, ha="center")
    ax.margins(0.15)
    ax.set_xlabel("Average price (USD)")
    ax.set_ylabel("Average review sentiment (VADER)")
    ax.set_title("Brand positioning – price vs customer sentiment (bubble = loves)")
    fig.tight_layout()
    fig.savefig(FIG / "brand_positioning.png", dpi=150)
    plt.close(fig)

    # 2. Popularity by category and price band
    pivot = cats.pivot_table(index="primary_category", columns="price_band", values="total_loves", aggfunc="sum").fillna(0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    pivot.plot.barh(stacked=True, ax=ax, colormap="Blues")
    ax.set_xlabel("Total loves")
    ax.set_ylabel("")
    ax.set_title("Where customer love goes – category x price band")
    ax.legend(title="Price band", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "category_price_band.png", dpi=150)
    plt.close(fig)

    # 3. Monthly trend of negative reviews
    monthly["negatives"] = monthly["negative_share"] * monthly["reviews"]
    trend = monthly.groupby("review_month")[["reviews", "negatives"]].sum()
    trend["negative_share"] = trend["negatives"] / trend["reviews"]
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.bar(trend.index, trend["reviews"], width=20, color=GREY, label="Reviews")
    ax1.set_ylabel("Reviews per month")
    ax2 = ax1.twinx()
    ax2.plot(trend.index, trend["negative_share"] * 100, color=ORANGE, lw=2, label="% negative")
    ax2.set_ylabel("% negative reviews")
    ax1.set_title("Review volume and share of negative reviews per month")
    fig.tight_layout()
    fig.savefig(FIG / "monthly_trend.png", dpi=150)
    plt.close(fig)

    # Insights computed from the data
    best = brands[brands["reviews"] >= brands["reviews"].median()].nlargest(1, "recommendation_rate").iloc[0]
    worst = brands[brands["reviews"] >= brands["reviews"].median()].nlargest(1, "negative_share").iloc[0]
    top_cat = cats.groupby("primary_category")["total_loves"].sum().idxmax()
    hidden = products[(products["avg_sentiment"] > products["avg_sentiment"].quantile(0.9))
                      & (products["loves_count"] < products["loves_count"].median())]
    lines = [
        "# Dashboard insights", "",
        f"- **{top_cat}** is the most loved category ({cats.groupby('primary_category')['total_loves'].sum().max():,.0f} loves).",
        f"- **{best['brand_name']}** has the highest recommendation rate among well-reviewed brands "
        f"({best['recommendation_rate']:.0%}).",
        f"- **{worst['brand_name']}** has the highest share of negative reviews ({worst['negative_share']:.0%}): "
        "investigate product quality and the claims in its descriptions.",
        f"- **{len(hidden)} hidden gems**: products in the top 10% for sentiment but below median popularity – "
        "candidates for visibility campaigns.",
    ]
    (ROOT / "dashboard" / "insights.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
