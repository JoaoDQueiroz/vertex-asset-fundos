import pandas as pd
import pytest

from rcap_fundos.core.kpi_janela import agregar_janela, pct_variacao


def test_agregar_janela_filtra_fundos():
    df = pd.DataFrame(
        {
            "DATA_REFERENCIA": pd.to_datetime(["2025-03-01", "2025-03-14", "2025-03-14"]),
            "FUNDO": ["A", "A", "B"],
            "SALDO_CC": [1.0, 2.0, 3.0],
            "APLICACOES_RF": [1.0, 1.0, 1.0],
            "CAPTACAO_LIQUIDA": [0.0, 100.0, 50.0],
            "COTISTAS_ATIVOS": [10, 10, 5],
        }
    )
    r = agregar_janela(df, ["A"], pd.Timestamp("2025-03-14"), 30)
    assert r["pl"] == 3.0
    assert r["captacao"] == pytest.approx(100.0)
    assert r["cotistas"] == 10


def test_pct_variacao():
    assert pct_variacao(110.0, 100.0) == pytest.approx(10.0)
