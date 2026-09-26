import json

import pandas as pd

from src import config
from src.agent.orchestrator import build_context, to_json_context
from src.profiling.pipeline import build_profile


def _sample_df(n_rows: int = 30) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "idade": list(range(20, 20 + n_rows)),
            "categoria": ["A", "B"] * (n_rows // 2),
            "data_evento": pd.date_range("2024-01-01", periods=n_rows, freq="D"),
        }
    )


def test_build_context_never_includes_more_rows_than_configured_sample_size(monkeypatch):
    monkeypatch.setattr(config, "SAMPLE_ROWS_FOR_AGENT", 5)
    df = _sample_df(30)
    profile = build_profile(df)

    context = build_context(profile, df)

    assert len(context["sample"]) == 5


def test_build_context_is_json_serializable_for_all_supported_column_types():
    df = _sample_df(10)
    profile = build_profile(df)

    context = build_context(profile, df)
    serialized = to_json_context(context)
    parsed = json.loads(serialized)

    assert parsed["overview"]["n_rows"] == 10
    assert "idade" in parsed["schema"]


def test_build_context_serializes_null_values_as_none():
    df = pd.DataFrame({"valor": [1.0, None, 3.0]})
    profile = build_profile(df)

    context = build_context(profile, df)
    parsed = json.loads(to_json_context(context))

    sample_values = [row["valor"] for row in parsed["sample"]]
    assert None in sample_values


def test_build_context_includes_quality_alerts_and_correlation_pairs():
    df = _sample_df(10)
    profile = build_profile(df)

    context = build_context(profile, df)

    assert "quality_alerts" in context
    assert "high_correlation_pairs" in context
