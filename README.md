# Stack Overflow Monitoring

A data pipeline and analysis toolkit that tracks technology adoption trends using Stack Overflow's public data dump, annual Developer Survey, and PyPI download statistics.

Built for **lowhangingdata** — skeptical, data-backed analysis aimed at analytics directors and data practitioners.

---

## What It Does

| Signal | Source | Insight |
|--------|--------|---------|
| Technology usage gaps | SO Developer Survey | "Used professionally" vs "Want to learn" delta |
| Community momentum | SO public data dump | Question volume, answer rates, tag velocity |
| Ecosystem growth | PyPI download stats | Real adoption vs marketing noise |
| dbt package trends | dbt Hub registry | Which data tools are actually growing |

### Flagship Analysis: The Hype Gap

The core output is a ranked table of technologies sorted by the gap between developer desire and professional reality — the things engineers *want* to use but companies haven't adopted yet (or the inverse: tools everyone is paid to use but no one wants to learn).

---

## Project Structure

```
stackoverflow-monitoring/
├── src/
│   ├── stackoverflow_monitor.py   # SO public API + data dump ingestion
│   ├── survey_analyzer.py         # Developer Survey gap analysis
│   ├── pypi_monitor.py            # PyPI download trend fetching
│   ├── dbt_monitor.py             # dbt Hub package registry scraper
│   ├── gap_analyzer.py            # "Used professionally" vs "Want to learn" engine
│   └── report_generator.py        # Markdown / CSV report output
├── data/
│   ├── raw/                       # Unmodified source data
│   └── processed/                 # Cleaned, joined datasets
├── reports/                       # Generated analysis outputs
├── notebooks/                     # Exploratory Jupyter notebooks
├── tests/                         # Unit tests
├── config.py                      # API keys, paths, thresholds
├── main.py                        # CLI entry point
└── requirements.txt
```

---

## Quickstart

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

Copy and edit the config:

```bash
cp config.example.py config_local.py
```

Set your Stack Overflow API key (free at [stackapps.com](https://stackapps.com)):

```python
SO_API_KEY = "your_key_here"
```

### 3. Run the full pipeline

```bash
python main.py --all
```

Or run individual modules:

```bash
# Technology hype-gap report (requires survey CSV)
python main.py --survey path/to/survey_results.csv

# PyPI download trends for a list of packages
python main.py --pypi dbt-core,sqlmesh,dagster,prefect,airflow

# Stack Overflow tag velocity (last 90 days)
python main.py --so-tags pandas,polars,duckdb,spark

# Full dbt Hub package growth report
python main.py --dbt
```

---

## Data Sources

### Stack Overflow Developer Survey
- Download: [insights.stackoverflow.com/survey](https://insights.stackoverflow.com/survey)
- Annual CSV, ~65k respondents
- Key columns: `LanguageHaveWorkedWith`, `LanguageWantToWorkWith`, `DatabaseHaveWorkedWith`, etc.

### Stack Overflow Public Data Dump
- Available via [data.stackexchange.com](https://data.stackexchange.com) (SEDE) or archive.org
- Tables used: `Tags`, `Posts`, `PostTags`
- Refresh: quarterly

### PyPI Download Stats
- Powered by [pypistats.org](https://pypistats.org) public API
- No auth required
- 180-day rolling window

### dbt Hub
- Public registry at [hub.getdbt.com](https://hub.getdbt.com)
- Package metadata and download counts

---

## Example Output

```
=== Technology Hype Gap Report (2024 Survey) ===

Rank  Technology     Want%   Used%   Gap    Signal
----  ----------     -----   -----   ---    ------
1     Rust           29.7%   8.3%    +21.4  High desire, low adoption
2     Kotlin         18.2%   9.1%    +9.1   Growing mobile/backend interest
3     Go             22.4%   13.8%   +8.6   DevOps pull
...
-3    MATLAB         1.2%    7.8%    -6.6   Legacy lock-in
-2    PHP            3.1%    11.2%   -8.1   Inherited codebases
-1    Cobol          0.4%    9.3%    -8.9   Maximum regret
```

---

## Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `SO_API_KEY` | `""` | Stack Overflow API key (increases rate limits) |
| `SO_PAGE_SIZE` | `100` | Results per API page |
| `PYPI_PACKAGES` | `[...]` | Default package list for PyPI monitoring |
| `SURVEY_PATH` | `data/raw/survey_results.csv` | Path to downloaded survey CSV |
| `REPORT_FORMAT` | `"markdown"` | Output format: `markdown`, `csv`, or `json` |
| `LOOKBACK_DAYS` | `90` | SO API tag activity window |

---

## Tests

```bash
pytest tests/ -v
```

---

## Contributing

1. Branch from `main`
2. Keep analysis reproducible — pin data source versions in commit messages
3. New data sources go in `src/`, one module per source
4. All monetary/percentage claims need a source URL in the report output
