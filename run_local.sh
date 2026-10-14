#!/usr/bin/env bash
# Run the full pipeline locally on DuckDB (no Docker, no Airflow) – useful for a quick test.
set -euo pipefail
cd "$(dirname "$0")"

export WAREHOUSE_URL="duckdb:///$(pwd)/sephora.duckdb"
export DUCKDB_PATH="$(pwd)/sephora.duckdb"

(cd src && python extract_load.py && python sentiment.py)
(cd dbt && dbt build --profiles-dir . --target duckdb)
(cd src && python export_marts.py && python dashboard_preview.py)

echo "Done: marts in sephora.duckdb, CSV exports in dashboard/exports/, charts in dashboard/preview/"
