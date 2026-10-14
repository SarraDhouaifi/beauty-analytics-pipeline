"""Shared settings. The warehouse connection comes from the WAREHOUSE_URL environment variable."""
import os
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv("DATA_DIR", ROOT / "data"))
EXPORTS = ROOT / "dashboard" / "exports"

# PostgreSQL by default (see docker/docker-compose.yml).
# For a quick local test without Docker: WAREHOUSE_URL=duckdb:///sephora.duckdb
WAREHOUSE_URL = os.getenv("WAREHOUSE_URL", "postgresql+psycopg2://sephora:sephora@localhost:5432/sephora")


def get_engine():
    engine = create_engine(WAREHOUSE_URL)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    return engine


def drop_table(engine, table: str) -> None:
    """Drop before to_sql: pandas' if_exists="replace" reflects the table first, and SQLAlchemy's
    PostgreSQL reflection queries pg_catalog tables that DuckDB does not emulate (pg_collation)."""
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
