import numpy as np
import pandas as pd
import pytest

from src import config
from src.profiling.correlations import (
    cramers_v,
    compute_correlation_matrices,
    find_high_correlation_pairs,
)


def test_compute_correlation_matrices_detects_perfect_pearson_correlation():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 4, 6, 8, 10]})

    result = compute_correlation_matrices(df)

    assert result["pearson"].loc["a", "b"] == pytest.approx(1.0)


def test_compute_correlation_matrices_detects_spearman_monotonic_correlation():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 4, 9, 16, 25]})

    result = compute_correlation_matrices(df)

    assert result["spearman"].loc["a", "b"] == pytest.approx(1.0)


def test_compute_correlation_matrices_ignores_non_numeric_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "cat": ["x", "y", "z"]})

    result = compute_correlation_matrices(df)

    assert "cat" not in result["pearson"].columns


def test_compute_correlation_matrices_truncates_above_column_cap(monkeypatch):
    monkeypatch.setattr(config, "MAX_CORRELATION_COLUMNS", 3)
    df = pd.DataFrame({f"col_{i}": np.arange(5) + i for i in range(5)})

    result = compute_correlation_matrices(df)

    assert result["truncated"] is True
    assert result["pearson"].shape == (3, 3)


def test_find_high_correlation_pairs_flags_pairs_above_threshold():
    matrix = pd.DataFrame(
        {"a": [1.0, 0.9, 0.1], "b": [0.9, 1.0, 0.05], "c": [0.1, 0.05, 1.0]},
        index=["a", "b", "c"],
    )

    pairs = find_high_correlation_pairs(matrix, threshold=0.7)

    assert len(pairs) == 1
    assert {pairs[0]["col_a"], pairs[0]["col_b"]} == {"a", "b"}


def test_cramers_v_is_high_for_perfectly_associated_categories():
    series_a = pd.Series(["x", "x", "y", "y"] * 200)
    series_b = pd.Series(["p", "p", "q", "q"] * 200)

    result = cramers_v(series_a, series_b)

    assert result > 0.95


def test_cramers_v_is_low_for_independent_categories():
    rng = np.random.default_rng(0)
    series_a = pd.Series(rng.choice(["x", "y"], size=300))
    series_b = pd.Series(rng.choice(["p", "q"], size=300))

    result = cramers_v(series_a, series_b)

    assert result < 0.3
