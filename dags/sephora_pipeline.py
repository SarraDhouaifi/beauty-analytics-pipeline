"""Airflow DAG: weekly refresh of the Sephora beauty analytics warehouse.

extract_load -> sentiment_scoring -> dbt_run -> dbt_test -> export_marts
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"
DBT = f"cd {PROJECT}/dbt && dbt {{cmd}} --profiles-dir . --target postgres"

default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sephora_beauty_pipeline",
    description="Load Sephora products and reviews, score sentiment, build dbt marts for Power BI",
    start_date=datetime(2026, 1, 1),
    schedule="@weekly",
    catchup=False,
    default_args=default_args,
    tags=["beauty", "dbt", "postgres"],
) as dag:

    extract_load = BashOperator(
        task_id="extract_load",
        bash_command=f"cd {PROJECT}/src && python extract_load.py",
    )

    sentiment_scoring = BashOperator(
        task_id="sentiment_scoring",
        bash_command=f"cd {PROJECT}/src && python sentiment.py",
    )

    dbt_run = BashOperator(task_id="dbt_run", bash_command=DBT.format(cmd="run"))

    # Data quality gate: the marts are only exported if every dbt test passes
    dbt_test = BashOperator(task_id="dbt_test", bash_command=DBT.format(cmd="test"))

    export_marts = BashOperator(
        task_id="export_marts",
        bash_command=f"cd {PROJECT}/src && python export_marts.py",
    )

    extract_load >> sentiment_scoring >> dbt_run >> dbt_test >> export_marts
