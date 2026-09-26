import pandas as pd

from src.profiling.categorical import compute_categorical_stats, detect_rare_categories


def _series() -> pd.Series:
    return pd.Series(["A"] * 180 + ["B"] * 15 + ["C"] * 4 + ["D"] * 1)


def test_compute_categorical_stats_reports_cardinality_and_mode():
    stats = compute_categorical_stats(_series())

    assert stats["cardinality"] == 4
    assert stats["mode"] == "A"


def test_compute_categorical_stats_top_frequencies_sorted_desc():
    stats = compute_categorical_stats(_series())

    top = list(stats["top_frequencies"].items())
    assert top[0] == ("A", 180)
    assert top[1] == ("B", 15)


def test_compute_categorical_stats_ignores_nulls():
    series = pd.Series(["A", "A", None, "B"])

    stats = compute_categorical_stats(series)

    assert stats["cardinality"] == 2


def test_detect_rare_categories_flags_categories_below_threshold():
    rare = detect_rare_categories(_series())

    assert rare == ["D"]


def test_detect_rare_categories_returns_empty_when_none_rare():
    series = pd.Series(["A"] * 5 + ["B"] * 5)

    rare = detect_rare_categories(series)

    assert rare == []
