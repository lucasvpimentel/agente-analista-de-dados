import numpy as np
import pandas as pd
import pytest

from src.profiling.numeric import (
    compute_numeric_stats,
    detect_outliers_iqr,
    detect_outliers_zscore,
)


@pytest.fixture
def series_with_outlier() -> pd.Series:
    return pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])


def test_compute_numeric_stats_matches_numpy_scipy_reference(series_with_outlier):
    stats = compute_numeric_stats(series_with_outlier)

    assert stats["mean"] == pytest.approx(series_with_outlier.mean())
    assert stats["median"] == pytest.approx(series_with_outlier.median())
    assert stats["std"] == pytest.approx(series_with_outlier.std())
    assert stats["min"] == 1
    assert stats["max"] == 100
    assert stats["q1"] == pytest.approx(series_with_outlier.quantile(0.25))
    assert stats["q3"] == pytest.approx(series_with_outlier.quantile(0.75))
    assert stats["iqr"] == pytest.approx(stats["q3"] - stats["q1"])
    assert stats["skewness"] == pytest.approx(series_with_outlier.skew())
    assert stats["kurtosis"] == pytest.approx(series_with_outlier.kurt())


def test_compute_numeric_stats_counts_zeros_and_negatives():
    series = pd.Series([-2, -1, 0, 0, 1, 2])

    stats = compute_numeric_stats(series)

    assert stats["n_zeros"] == 2
    assert stats["n_negatives"] == 2


def test_detect_outliers_iqr_finds_the_extreme_value(series_with_outlier):
    result = detect_outliers_iqr(series_with_outlier)

    assert result["count"] == 1
    assert 9 in result["indices"]


def test_detect_outliers_iqr_finds_none_in_uniform_data():
    series = pd.Series([10, 11, 12, 13, 14, 15])

    result = detect_outliers_iqr(series)

    assert result["count"] == 0
    assert result["indices"] == []


def test_detect_outliers_zscore_finds_the_extreme_value():
    series = pd.Series(list(range(1, 21)) + [200])

    result = detect_outliers_zscore(series)

    assert result["count"] == 1
    assert 20 in result["indices"]


def test_detect_outliers_zscore_handles_zero_std_without_error():
    series = pd.Series([5, 5, 5, 5])

    result = detect_outliers_zscore(series)

    assert result["count"] == 0
    assert result["indices"] == []


def test_numeric_functions_ignore_nulls():
    series = pd.Series([1, 2, np.nan, 3, 4])

    stats = compute_numeric_stats(series)

    assert stats["mean"] == pytest.approx(2.5)
