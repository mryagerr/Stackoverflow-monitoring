import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

SO_API_KEY = os.getenv("SO_API_KEY", "")
SO_API_BASE = "https://api.stackexchange.com/2.3"
SO_PAGE_SIZE = 100
LOOKBACK_DAYS = 90

SURVEY_PATH = RAW_DIR / "survey_results.csv"

PYPI_API_BASE = "https://pypistats.org/api"
PYPI_PACKAGES = [
    "dbt-core",
    "sqlmesh",
    "dagster",
    "prefect",
    "apache-airflow",
    "kedro",
    "polars",
    "duckdb",
    "pandas",
    "pyspark",
]

DBT_HUB_API = "https://hub.getdbt.com/api/v1"

REPORT_FORMAT = os.getenv("REPORT_FORMAT", "markdown")

SO_TAG_GROUPS = {
    "data_warehousing": ["dbt", "snowflake", "bigquery", "redshift", "databricks"],
    "orchestration": ["airflow", "prefect", "dagster", "kedro"],
    "dataframe": ["pandas", "polars", "dask", "spark"],
    "query_engines": ["duckdb", "trino", "presto", "athena"],
    "languages": ["python", "sql", "r", "scala", "julia"],
}
