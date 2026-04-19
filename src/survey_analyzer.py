"""Parses the Stack Overflow annual Developer Survey CSV to compute adoption gaps."""

from pathlib import Path

import pandas as pd

import config

# Survey column names vary slightly by year; these are the canonical 2023/2024 names.
_HAVE_COLS = [
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "PlatformHaveWorkedWith",
    "WebframeHaveWorkedWith",
    "MiscTechHaveWorkedWith",
    "ToolsTechHaveWorkedWith",
]

_WANT_COLS = [
    "LanguageWantToWorkWith",
    "DatabaseWantToWorkWith",
    "PlatformWantToWorkWith",
    "WebframeWantToWorkWith",
    "MiscTechWantToWorkWith",
    "ToolsTechWantToWorkWith",
]


def _count_mentions(series: pd.Series) -> pd.Series:
    """Split semicolon-delimited cells and count mentions per technology."""
    exploded = series.dropna().str.split(";").explode().str.strip()
    return exploded.value_counts()


def load_survey(path: Path = config.SURVEY_PATH) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def compute_gap(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each technology, compute:
      - pct_have: % of respondents who used it professionally
      - pct_want: % who want to learn / use it next year
      - gap: pct_want - pct_have  (positive = desire exceeds reality)
    """
    n = len(df)
    have_cols = [c for c in _HAVE_COLS if c in df.columns]
    want_cols = [c for c in _WANT_COLS if c in df.columns]

    have_counts = pd.concat([_count_mentions(df[c]) for c in have_cols]).groupby(level=0).sum()
    want_counts = pd.concat([_count_mentions(df[c]) for c in want_cols]).groupby(level=0).sum()

    all_techs = have_counts.index.union(want_counts.index)
    result = pd.DataFrame(index=all_techs)
    result["mentions_have"] = have_counts.reindex(all_techs, fill_value=0)
    result["mentions_want"] = want_counts.reindex(all_techs, fill_value=0)
    result["pct_have"] = (result["mentions_have"] / n * 100).round(2)
    result["pct_want"] = (result["mentions_want"] / n * 100).round(2)
    result["gap"] = (result["pct_want"] - result["pct_have"]).round(2)
    result.index.name = "technology"

    return result.sort_values("gap", ascending=False).reset_index()


def top_gaps(df: pd.DataFrame, n: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return top n desired (positive gap) and top n regret (negative gap) technologies."""
    gaps = compute_gap(df)
    desired = gaps[gaps["gap"] > 0].head(n)
    regret = gaps[gaps["gap"] < 0].sort_values("gap").head(n)
    return desired, regret
