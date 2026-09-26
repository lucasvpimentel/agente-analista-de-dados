import pandas as pd

from src.profiling.types import infer_types


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "idade": [25, 30, 35, 40, 45],
            "categoria": ["A", "B", "A", "B", "A"],
            "data_evento": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "comentario": [
                "Entrega atrasou bastante e o suporte demorou pra responder",
                "Produto excelente, chegou antes do prazo combinado",
                "Embalagem veio danificada mas o item estava intacto",
                "Atendimento rápido, resolveram tudo numa única ligação",
                "Preço justo e qualidade acima do esperado pelo valor pago",
            ],
            "id_cliente": ["C001", "C002", "C003", "C004", "C005"],
            "ativo": [True, False, True, False, True],
        }
    )


def test_infer_types_detects_all_six_types():
    types = infer_types(_sample_df())

    assert types["idade"] == "numerica"
    assert types["categoria"] == "categorica"
    assert types["data_evento"] == "data"
    assert types["comentario"] == "texto_livre"
    assert types["id_cliente"] == "id"
    assert types["ativo"] == "booleana"


def test_infer_types_respects_manual_override():
    types = infer_types(_sample_df(), overrides={"idade": "categorica"})

    assert types["idade"] == "categorica"
    assert types["categoria"] == "categorica"
