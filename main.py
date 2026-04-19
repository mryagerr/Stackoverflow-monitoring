"""CLI entry point for the Stack Overflow monitoring pipeline."""

import sys
from pathlib import Path

import click
from rich.console import Console

import config
from src.stackoverflow_monitor import StackOverflowMonitor
from src.pypi_monitor import PyPIMonitor
from src.dbt_monitor import DbtHubMonitor
from src.report_generator import render_survey_gap, render_so_velocity, render_pypi, print_summary

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--all", "run_all", is_flag=True, help="Run the full pipeline.")
@click.option("--survey", type=click.Path(exists=True), help="Path to SO survey CSV.")
@click.option("--pypi", "pypi_packages", default=None, help="Comma-separated package list.")
@click.option("--so-tags", default=None, help="Comma-separated SO tag list.")
@click.option("--dbt", is_flag=True, help="Run dbt Hub analysis.")
@click.option("--format", "fmt", default=config.REPORT_FORMAT, type=click.Choice(["markdown", "csv", "json"]))
def cli(ctx, run_all, survey, pypi_packages, so_tags, dbt, fmt):
    """Stack Overflow & ecosystem monitoring pipeline."""
    if ctx.invoked_subcommand is not None:
        return

    ran_something = False

    if survey or run_all:
        survey_path = Path(survey) if survey else config.SURVEY_PATH
        if not survey_path.exists():
            console.print(f"[yellow]Survey file not found: {survey_path}[/yellow]")
            console.print("Download from https://insights.stackoverflow.com/survey and set SURVEY_PATH in config.py")
        else:
            from src.survey_analyzer import load_survey, top_gaps
            console.print("[bold]Running survey gap analysis...[/bold]")
            df = load_survey(survey_path)
            desired, regret = top_gaps(df)
            render_survey_gap(desired, regret, fmt=fmt)
            ran_something = True

    if so_tags or run_all:
        tags = [t.strip() for t in so_tags.split(",")] if so_tags else list(config.SO_TAG_GROUPS["data_warehousing"])
        console.print(f"[bold]Fetching SO tag velocity for:[/bold] {tags}")
        monitor = StackOverflowMonitor()
        velocity = monitor.get_tag_velocity(tags)
        render_so_velocity(velocity, fmt=fmt)
        ran_something = True
    else:
        velocity = []

    if pypi_packages or run_all:
        pkgs = [p.strip() for p in pypi_packages.split(",")] if pypi_packages else config.PYPI_PACKAGES
        console.print(f"[bold]Fetching PyPI stats for {len(pkgs)} packages...[/bold]")
        pypi = PyPIMonitor()
        stats = pypi.bulk_recent(pkgs)
        render_pypi(stats, fmt=fmt)
        ran_something = True
    else:
        stats = []

    if dbt or run_all:
        console.print("[bold]Fetching dbt Hub packages...[/bold]")
        hub = DbtHubMonitor()
        top = hub.top_packages()
        console.print(top)
        ran_something = True

    if velocity or stats:
        print_summary(velocity, stats)

    if not ran_something:
        click.echo(ctx.get_help())


if __name__ == "__main__":
    cli()
