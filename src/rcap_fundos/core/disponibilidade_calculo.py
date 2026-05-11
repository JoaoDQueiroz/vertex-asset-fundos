"""Cálculos de disponibilidade de caixa (camada sem I/O)."""

from __future__ import annotations

import pandas as pd

COL_DESPESAS = [
    "AUDITORIA",
    "AUDITORIA_PEND",
    "TX_GESTAO",
    "TX_GESTAO_PEND",
    "TX_ADM",
    "TX_ADM_PEND",
    "TX_ESCRITURACAO",
    "TX_ESCRITURACAO_PEND",
    "TX_CUSTODIA",
    "TX_CUSTODIA_PEND",
    "BANCO_LIQ",
    "BANCO_LIQ_PEND",
    "TX_CVM",
    "TX_CVM_PEND",
    "TX_CETIP",
    "TX_CETIP_PEND",
    "TX_ANBIMA",
    "TX_ANBIMA_PEND",
    "OUTROS",
]


def enriquecer_disponibilidade(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta colunas DESPESAS (soma das rubricas existentes) e DISPONIBILIDADE."""
    out = df.copy()
    existentes = [c for c in COL_DESPESAS if c in out.columns]
    if existentes:
        out["DESPESAS"] = out[existentes].sum(axis=1)
    else:
        out["DESPESAS"] = 0.0
    out["DISPONIBILIDADE"] = out["SALDO_CC"] + out["APLICACOES_RF"] + out["DESPESAS"]
    return out
