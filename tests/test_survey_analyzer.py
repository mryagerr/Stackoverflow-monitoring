"""Tests for survey gap computation."""

import pandas as pd
import pytest

from src.survey_analyzer import compute_gap, top_gaps


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "LanguageHaveWorkedWith": [
                "Python;SQL",
                "Python;Java",
                "Java;PHP",
                "SQL;PHP",
                "Python;SQL;Rust",
            ],
            "LanguageWantToWorkWith": [
                "Rust;Go",
                "Rust;Python",
                "Go;Kotlin",
                "Rust;Go",
                "Go",
            ],
        }
    )


def test_compute_gap_returns_all_techs(sample_df):
    result = compute_gap(sample_df)
    techs = set(result["technology"])
    assert "Python" in techs
    assert "Rust" in techs
    assert "Go" in techs


def test_gap_direction(sample_df):
    result = compute_gap(sample_df)
    rust = result[result["technology"] == "Rust"].iloc[0]
    # Rust appears in want more than have → positive gap
    assert rust["gap"] > 0

    php = result[result["technology"] == "PHP"].iloc[0]
    # PHP appears in have more than want → negative gap
    assert php["gap"] < 0


def test_top_gaps_returns_two_frames(sample_df):
    desired, regret = top_gaps(sample_df, n=5)
    assert isinstance(desired, pd.DataFrame)
    assert isinstance(regret, pd.DataFrame)
    assert (desired["gap"] > 0).all()
    assert (regret["gap"] < 0).all()


def test_pct_bounds(sample_df):
    result = compute_gap(sample_df)
    assert (result["pct_have"] >= 0).all()
    assert (result["pct_have"] <= 100).all()
    assert (result["pct_want"] >= 0).all()
    assert (result["pct_want"] <= 100).all()
