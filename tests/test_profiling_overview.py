import pandas as pd

from src.profiling.overview import compute_overview


def test_compute_overview_counts_rows_and_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    overview = compute_overview(df)

    assert overview["n_rows"] == 3
    assert overview["n_columns"] == 2


def test_compute_overview_counts_duplicate_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})

    overview = compute_overview(df)

    assert overview["n_duplicate_rows"] == 1


def test_compute_overview_computes_pct_null_total():
    df = pd.DataFrame({"a": [1, None, 3, None], "b": [1, 2, 3, 4]})

    overview = compute_overview(df)

    assert overview["pct_null_total"] == 25.0


def test_compute_overview_reports_memory_usage():
    df = pd.DataFrame({"a": [1, 2, 3]})

    overview = compute_overview(df)

    assert overview["memory_usage_bytes"] > 0
