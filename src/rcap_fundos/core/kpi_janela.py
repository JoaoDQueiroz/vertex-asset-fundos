"""Agregados por janela de datas para o painel de indicadores."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd


def dias_por_periodo(codigo: str) -> int:
    return {"1M": 30, "3M": 90, "6M": 180}.get(codigo, 30)


def _filtra(df: pd.DataFrame, fundos: list[str] | None, d0: pd.Timestamp, d1: pd.Timestamp) -> pd.DataFrame:
    m = (df["DATA_REFERENCIA"] >= d0) & (df["DATA_REFERENCIA"] <= d1)
    if fundos is not None and len(fundos) > 0:
        m &= df["FUNDO"].isin(fundos)
    return df.loc[m]


def agregar_janela(df: pd.DataFrame, fundos: list[str] | None, fim: pd.Timestamp, dias: int) -> dict:
    """Métricas no último dia da janela [fim - dias, fim] (intersecção com dados)."""
    inicio = fim - timedelta(days=dias)
    w = _filtra(df, fundos, inicio, fim)
    if w.empty:
        return {
            "pl": 0.0,
            "captacao": 0.0,
            "cotistas": 0,
            "n_fundos": 0,
            "ultimo_dia": None,
        }
    ultimo = w["DATA_REFERENCIA"].max()
    ult = w[w["DATA_REFERENCIA"] == ultimo]
    pl = float((ult["SALDO_CC"] + ult["APLICACOES_RF"]).sum())
    capt = float(w["CAPTACAO_LIQUIDA"].sum()) if "CAPTACAO_LIQUIDA" in w.columns else 0.0
    cot = int(ult["COTISTAS_ATIVOS"].sum()) if "COTISTAS_ATIVOS" in ult.columns else int(ult["FUNDO"].nunique() * 40)
    return {
        "pl": pl,
        "captacao": capt,
        "cotistas": cot,
        "n_fundos": int(ult["FUNDO"].nunique()),
        "ultimo_dia": ultimo,
    }


def agregar_janela_anterior(df: pd.DataFrame, fundos: list[str] | None, fim: pd.Timestamp, dias: int) -> dict:
    fim_prev = fim - timedelta(days=dias)
    inicio_prev = fim_prev - timedelta(days=dias)
    return agregar_janela(df, fundos, fim_prev, dias)


def pct_variacao(atual: float, anterior: float) -> float | None:
    if anterior == 0:
        return None
    return (atual - anterior) / abs(anterior) * 100.0
