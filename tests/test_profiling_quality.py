import pandas as pd

from src.profiling.quality import (
    constant_columns,
    duplicate_row_count,
    generate_alerts,
    near_unique_columns,
    null_percentages,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sempre_nulo": [None, None, None, None, None],
            "constante": [7, 7, 7, 7, 7],
            "quase_unico": ["a1", "a2", "a3", "a4", "a5"],
            "normal": [1, 2, 2, 3, 4],
        }
    )


def test_null_percentages_flags_fully_null_column():
    percentages = null_percentages(_sample_df())

    assert percentages["sempre_nulo"] == 100.0
    assert percentages["normal"] == 0.0


def test_constant_columns_detects_single_value_column():
    result = constant_columns(_sample_df())

    assert result == ["constante"]


def test_near_unique_columns_detects_high_cardinality_column():
    result = near_unique_columns(_sample_df())

    assert result == ["quase_unico"]


def test_duplicate_row_count_counts_repeated_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})

    assert duplicate_row_count(df) == 1


def test_generate_alerts_flags_all_quality_issues():
    alerts = generate_alerts(_sample_df())

    columns_flagged = {alert["column"] for alert in alerts}
    assert "sempre_nulo" in columns_flagged
    assert "constante" in columns_flagged
    assert "quase_unico" in columns_flagged
    assert "normal" not in columns_flagged


def test_generate_alerts_sorted_by_severity_highest_first():
    alerts = generate_alerts(_sample_df())

    severities = [alert["severity"] for alert in alerts]
    severity_rank = {"alta": 0, "media": 1, "baixa": 2}
    ranks = [severity_rank[s] for s in severities]

    assert ranks == sorted(ranks)
    assert alerts[0]["column"] == "sempre_nulo"
    assert alerts[0]["severity"] == "alta"
