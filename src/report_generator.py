"""Renders analysis results to Markdown, CSV, or JSON."""

import json
from datetime import date
from pathlib import Path
from typing import Literal

import pandas as pd
from rich.console import Console
from rich.table import Table

import config

console = Console()


def _survey_gap_table(desired: pd.DataFrame, regret: pd.DataFrame) -> str:
    lines = [
        f"# Technology Hype Gap Report — {date.today().isoformat()}\n",
        "## Technologies Developers WANT But Aren't Using Professionally\n",
        "| Rank | Technology | Want% | Used% | Gap |",
        "|------|-----------|-------|-------|-----|",
    ]
    for i, row in desired.iterrows():
        lines.append(f"| {i+1} | {row['technology']} | {row['pct_want']}% | {row['pct_have']}% | +{row['gap']}% |")

    lines += [
        "\n## Technologies Developers Use But Don't Want To (The Regret List)\n",
        "| Rank | Technology | Used% | Want% | Gap |",
        "|------|-----------|-------|-------|-----|",
    ]
    for i, row in regret.iterrows():
        lines.append(f"| {i+1} | {row['technology']} | {row['pct_have']}% | {row['pct_want']}% | {row['gap']}% |")

    return "\n".join(lines)


def _so_velocity_table(velocity: list[dict], lookback: int) -> str:
    lines = [
        f"# Stack Overflow Tag Velocity — Last {lookback} Days\n",
        "| Tag | Total Questions | Recent Questions | Daily Rate |",
        "|-----|----------------|-----------------|------------|",
    ]
    for row in velocity:
        lines.append(
            f"| {row['tag']} | {row['total_questions']:,} "
            f"| {row.get(f'questions_last_{lookback}d', '—')} "
            f"| {row['daily_rate']}/day |"
        )
    return "\n".join(lines)


def _pypi_table(stats: list[dict]) -> str:
    lines = [
        "# PyPI Download Stats\n",
        "| Package | Last Day | Last Week | Last Month |",
        "|---------|----------|-----------|------------|",
    ]
    for row in stats:
        if "error" in row:
            lines.append(f"| {row['package']} | error | error | error |")
        else:
            lines.append(
                f"| {row['package']} | {row['last_day']:,} "
                f"| {row['last_week']:,} | {row['last_month']:,} |"
            )
    return "\n".join(lines)


def render_survey_gap(
    desired: pd.DataFrame,
    regret: pd.DataFrame,
    fmt: Literal["markdown", "csv", "json"] = config.REPORT_FORMAT,
    out_dir: Path = config.REPORTS_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"hype_gap_{date.today().isoformat()}"

    if fmt == "markdown":
        content = _survey_gap_table(desired, regret)
        path = out_dir / f"{stem}.md"
        path.write_text(content)
    elif fmt == "csv":
        combined = pd.concat([desired.assign(type="desired"), regret.assign(type="regret")])
        path = out_dir / f"{stem}.csv"
        combined.to_csv(path, index=False)
        content = combined.to_csv(index=False)
    elif fmt == "json":
        payload = {"desired": desired.to_dict("records"), "regret": regret.to_dict("records")}
        path = out_dir / f"{stem}.json"
        content = json.dumps(payload, indent=2)
        path.write_text(content)

    console.print(f"[green]Report written:[/green] {path}")
    return path


def render_so_velocity(
    velocity: list[dict],
    lookback: int = config.LOOKBACK_DAYS,
    fmt: Literal["markdown", "csv", "json"] = config.REPORT_FORMAT,
    out_dir: Path = config.REPORTS_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"so_velocity_{date.today().isoformat()}"

    if fmt == "markdown":
        path = out_dir / f"{stem}.md"
        path.write_text(_so_velocity_table(velocity, lookback))
    elif fmt == "csv":
        path = out_dir / f"{stem}.csv"
        pd.DataFrame(velocity).to_csv(path, index=False)
    elif fmt == "json":
        path = out_dir / f"{stem}.json"
        path.write_text(json.dumps(velocity, indent=2))

    console.print(f"[green]Report written:[/green] {path}")
    return path


def render_pypi(
    stats: list[dict],
    fmt: Literal["markdown", "csv", "json"] = config.REPORT_FORMAT,
    out_dir: Path = config.REPORTS_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"pypi_{date.today().isoformat()}"

    if fmt == "markdown":
        path = out_dir / f"{stem}.md"
        path.write_text(_pypi_table(stats))
    elif fmt == "csv":
        path = out_dir / f"{stem}.csv"
        pd.DataFrame(stats).to_csv(path, index=False)
    elif fmt == "json":
        path = out_dir / f"{stem}.json"
        path.write_text(json.dumps(stats, indent=2))

    console.print(f"[green]Report written:[/green] {path}")
    return path


def print_summary(velocity: list[dict], pypi: list[dict]) -> None:
    table = Table(title="Quick Summary")
    table.add_column("Source")
    table.add_column("Top Technology")
    table.add_column("Signal")

    if velocity:
        top_so = velocity[0]
        table.add_row("Stack Overflow", top_so["tag"], f"{top_so['daily_rate']} q/day")
    if pypi:
        top_py = next((p for p in pypi if "error" not in p), {})
        if top_py:
            table.add_row("PyPI", top_py["package"], f"{top_py['last_month']:,}/mo")

    console.print(table)
