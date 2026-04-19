"""Tests for composite signal scoring."""

import pandas as pd

from src.gap_analyzer import build_signals, to_dataframe, _soft_norm


def test_soft_norm_positive():
    assert _soft_norm(10, 10) == pytest.approx(0.5)


def test_soft_norm_zero():
    assert _soft_norm(0, 10) == 0.0


def test_build_signals_no_crash():
    survey = pd.DataFrame([
        {"technology": "dbt", "gap": 5.0, "pct_have": 10.0, "pct_want": 15.0},
        {"technology": "airflow", "gap": -3.0, "pct_have": 12.0, "pct_want": 9.0},
    ])
    so = [{"tag": "dbt", "daily_rate": 4.5, "total_questions": 10000}]
    pypi = [{"package": "dbt-core", "last_month": 500000}]

    signals = build_signals(survey, so, pypi)
    assert len(signals) >= 2


def test_to_dataframe():
    survey = pd.DataFrame([{"technology": "polars", "gap": 8.0, "pct_have": 5.0, "pct_want": 13.0}])
    signals = build_signals(survey, [], [])
    df = to_dataframe(signals)
    assert "technology" in df.columns
    assert "composite_score" in df.columns


import pytest
