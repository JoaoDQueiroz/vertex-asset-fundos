import pandas as pd
import pytest

from rcap_fundos.core.disponibilidade_calculo import COL_DESPESAS, enriquecer_disponibilidade


def test_enriquecer_disponibilidade_soma_despesas():
    df = pd.DataFrame(
        {
            "FUNDO": ["A"],
            "SALDO_CC": [1_000_000.0],
            "APLICACOES_RF": [100_000.0],
            "AUDITORIA": [-500.0],
            "TX_ADM": [-300.0],
        }
    )
    out = enriquecer_disponibilidade(df)
    assert out["DESPESAS"].iloc[0] == pytest.approx(-800.0)
    assert out["DISPONIBILIDADE"].iloc[0] == pytest.approx(1_000_000.0 + 100_000.0 - 800.0)


def test_enriquecer_sem_colunas_de_despesa():
    df = pd.DataFrame({"FUNDO": ["X"], "SALDO_CC": [10.0], "APLICACOES_RF": [5.0]})
    out = enriquecer_disponibilidade(df)
    assert out["DESPESAS"].iloc[0] == 0.0
    assert out["DISPONIBILIDADE"].iloc[0] == pytest.approx(15.0)


def test_lista_despesas_tem_rubricas_esperadas():
    assert "OUTROS" in COL_DESPESAS
    assert len(COL_DESPESAS) == 19
