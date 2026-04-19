"""
Combines survey gap data with SO tag velocity and PyPI stats
to produce a unified technology signal score.
"""

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class TechSignal:
    technology: str
    survey_gap: Optional[float] = None       # pct_want - pct_have (survey)
    pct_have: Optional[float] = None
    pct_want: Optional[float] = None
    so_daily_rate: Optional[float] = None    # SO questions/day (recent window)
    so_total_questions: Optional[int] = None
    pypi_last_month: Optional[int] = None
    composite_score: float = 0.0


def build_signals(
    survey_gaps: pd.DataFrame,
    so_velocity: list[dict],
    pypi_recent: list[dict],
) -> list[TechSignal]:
    """
    Join survey, SO, and PyPI data on technology name (case-insensitive).
    Returns a list of TechSignal objects sorted by composite_score descending.
    """
    survey_map = {row["technology"].lower(): row for _, row in survey_gaps.iterrows()}
    so_map = {row["tag"].lower(): row for row in so_velocity}
    pypi_map = {row["package"].lower(): row for row in pypi_recent}

    all_techs = set(survey_map) | set(so_map) | set(pypi_map)
    signals = []

    for tech in all_techs:
        s = survey_map.get(tech, {})
        so = so_map.get(tech, {})
        py = pypi_map.get(tech, {})

        sig = TechSignal(technology=tech)
        sig.survey_gap = s.get("gap")
        sig.pct_have = s.get("pct_have")
        sig.pct_want = s.get("pct_want")
        sig.so_daily_rate = so.get("daily_rate")
        sig.so_total_questions = so.get("total_questions")
        sig.pypi_last_month = py.get("last_month")

        sig.composite_score = _score(sig)
        signals.append(sig)

    return sorted(signals, key=lambda x: x.composite_score, reverse=True)


def _score(sig: TechSignal) -> float:
    """
    Weighted composite. All inputs normalized to [0, 1] range via soft scaling.
    Weights are intentionally simple and easy to override.
    """
    score = 0.0
    if sig.survey_gap is not None:
        score += _soft_norm(sig.survey_gap, scale=20.0) * 0.5
    if sig.so_daily_rate is not None:
        score += _soft_norm(sig.so_daily_rate, scale=50.0) * 0.3
    if sig.pypi_last_month is not None:
        score += _soft_norm(sig.pypi_last_month, scale=5_000_000) * 0.2
    return round(score, 4)


def _soft_norm(value: float, scale: float) -> float:
    """Sigmoid-like normalization so outliers don't dominate."""
    return value / (abs(value) + scale)


def to_dataframe(signals: list[TechSignal]) -> pd.DataFrame:
    return pd.DataFrame([s.__dict__ for s in signals])
