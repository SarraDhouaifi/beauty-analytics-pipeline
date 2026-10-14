"""Score the sentiment of every review with VADER and store it in raw.review_sentiment.

VADER is a lexicon-based model built for short social-media style English text,
which fits product reviews and runs on a laptop without a GPU.
"""
import logging

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import drop_table, get_engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def label(score: float) -> str:
    # Standard VADER thresholds
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


def main() -> None:
    engine = get_engine()
    reviews = pd.read_sql("SELECT review_id, review_title, review_text FROM raw.reviews", engine)
    text_ = (reviews["review_title"].fillna("") + ". " + reviews["review_text"].fillna("")).str.strip(". ")

    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(t)["compound"] if t else 0.0 for t in text_]

    out = pd.DataFrame({"review_id": reviews["review_id"], "sentiment_score": scores})
    out["sentiment_label"] = out["sentiment_score"].map(label)
    drop_table(engine, "raw.review_sentiment")
    out.to_sql("review_sentiment", engine, schema="raw", if_exists="replace", index=False, chunksize=50_000)
    log.info("Scored %s reviews: %s", f"{len(out):,}", out["sentiment_label"].value_counts().to_dict())


if __name__ == "__main__":
    main()
