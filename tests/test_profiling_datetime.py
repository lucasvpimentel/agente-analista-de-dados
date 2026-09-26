import pandas as pd

from src.profiling.datetime_stats import (
    compute_datetime_stats,
    detect_gaps,
    detect_granularity,
)


def test_detect_granularity_identifies_daily_series():
    series = pd.Series(pd.date_range("2024-01-01", periods=10, freq="D"))

    assert detect_granularity(series) == "diaria"


def test_detect_granularity_identifies_monthly_series():
    series = pd.Series(pd.date_range("2024-01-01", periods=6, freq="MS"))

    assert detect_granularity(series) == "mensal"


def test_detect_gaps_finds_missing_daily_dates():
    dates = pd.date_range("2024-01-01", "2024-01-05", freq="D").tolist()
    dates.remove(pd.Timestamp("2024-01-03"))
    series = pd.Series(dates)

    gaps = detect_gaps(series)

    assert pd.Timestamp("2024-01-03") in gaps
    assert len(gaps) == 1


def test_detect_gaps_finds_missing_monthly_periods():
    dates = pd.date_range("2024-01-01", periods=5, freq="MS").tolist()
    dates.remove(pd.Timestamp("2024-03-01"))
    series = pd.Series(dates)

    gaps = detect_gaps(series)

    assert pd.Timestamp("2024-03-01") in gaps


def test_compute_datetime_stats_reports_min_max_and_granularity():
    series = pd.Series(pd.date_range("2024-01-01", periods=10, freq="D"))

    stats = compute_datetime_stats(series)

    assert stats["min"] == pd.Timestamp("2024-01-01")
    assert stats["max"] == pd.Timestamp("2024-01-10")
    assert stats["granularity"] == "diaria"
    assert stats["gaps"] == []


def test_compute_datetime_stats_counts_by_period():
    series = pd.Series(
        [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-20"), pd.Timestamp("2024-02-10")]
    )

    stats = compute_datetime_stats(series)

    assert stats["counts_by_period"]["2024-01"] == 2
    assert stats["counts_by_period"]["2024-02"] == 1
