import pandas as pd

from src.profiling.pipeline import build_profile


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "idade": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
            "categoria": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
            "data_evento": pd.date_range("2024-01-01", periods=10, freq="D"),
        }
    )


def test_build_profile_includes_overview_and_types():
    profile = build_profile(_sample_df())

    assert profile["overview"]["n_rows"] == 10
    assert profile["types"]["idade"] == "numerica"
    assert profile["types"]["categoria"] == "categorica"
    assert profile["types"]["data_evento"] == "data"


def test_build_profile_computes_numeric_column_stats():
    profile = build_profile(_sample_df())

    numeric_column = profile["columns"]["idade"]
    assert numeric_column["type"] == "numerica"
    assert "mean" in numeric_column
    assert "outliers_iqr" in numeric_column


def test_build_profile_computes_categorical_column_stats():
    profile = build_profile(_sample_df())

    categorical_column = profile["columns"]["categoria"]
    assert categorical_column["type"] == "categorica"
    assert "cardinality" in categorical_column
    assert "rare_categories" in categorical_column


def test_build_profile_computes_datetime_column_stats():
    profile = build_profile(_sample_df())

    date_column = profile["columns"]["data_evento"]
    assert date_column["type"] == "data"
    assert "granularity" in date_column


def test_build_profile_includes_quality_alerts_and_correlations():
    profile = build_profile(_sample_df())

    assert "quality_alerts" in profile
    assert "pearson" in profile["correlations"]
    assert isinstance(profile["high_correlation_pairs"], list)


def test_build_profile_converts_string_dates_before_datetime_stats():
    df = pd.DataFrame(
        {"data_evento": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"]}
    )

    profile = build_profile(df)

    assert profile["types"]["data_evento"] == "data"
    assert profile["columns"]["data_evento"]["granularity"] == "diaria"


def test_build_profile_respects_type_overrides():
    profile = build_profile(_sample_df(), overrides={"idade": "categorica"})

    assert profile["types"]["idade"] == "categorica"
    assert profile["columns"]["idade"]["type"] == "categorica"
    assert "cardinality" in profile["columns"]["idade"]
