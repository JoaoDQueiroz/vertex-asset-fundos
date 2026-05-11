"""Gera planilhas sintéticas em demo_data/ (uso com RCAP_DEMO=1)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo_data"


def _disponibilidade_rows():
    cols_desp = [
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
    fundos = [
        ("Fundo Aurora FIC FIM", "12.345.678/0001-90", "Admin Demo S.A.", 118),
        ("Fundo Horizonte Multimercado", "98.765.432/0001-10", "Admin Demo S.A.", 84),
        ("FIDC Exemplo Recebíveis", "11.222.333/0001-44", "Custódia Demo Ltda", 52),
    ]
    rows = []
    datas = pd.date_range(start="2025-01-03", end="2025-03-14", freq="7D")
    for di, d in enumerate(datas):
        dstr = d.strftime("%Y-%m-%d")
        for i, (fundo, cnpj, adm, cotistas) in enumerate(fundos):
            drift = float(di) * 9_000.0 + float(i) * 12_000.0
            base_cc = 1_180_000.0 + i * 320_000.0 + drift
            base_rf = 410_000.0 - i * 48_000.0 + drift * 0.15
            desp = {}
            for j, c in enumerate(cols_desp):
                desp[c] = -(750 + j * 115 + i * 28 + (45 if "_PEND" in c else 0))
            captacao = (di - 5) * 22_000.0 + (i - 1) * 8_500.0
            row = {
                "DATA_REFERENCIA": dstr,
                "FUNDO": fundo,
                "CNPJ": cnpj,
                "ADMINISTRADOR": adm,
                "SALDO_CC": base_cc,
                "APLICACOES_RF": base_rf,
                "COTISTAS_ATIVOS": cotistas,
                "CAPTACAO_LIQUIDA": captacao,
                **desp,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def _fundos_rows():
    return pd.DataFrame(
        [
            {
                "Tp_Fundo": "FIM",
                "CNPJ_Fundo": "12.345.678/0001-90",
                "Nome_Fundo": "Fundo Aurora FIC FIM",
                "Razão_Social": "FIDC Aurora Demonstração",
                "Situação": "Ativo",
                "Prazo_Liq_Fin": "D+2",
                "Exercício": "2025",
                "Admin": "Admin Demo S.A.",
                "Gestor": "Gestora Exemplo Ltda",
                "Auditor": "Auditoria Demo",
                "Custodiante": "Banco Demo S.A.",
                "Tx_Adm_Fixo": 0.15,
                "Tx_Adm_Mín": 0.05,
                "Tx_Adm_Var": 0.08,
                "Tx_Gest_Fixo": 0.20,
                "Tx_Gest_Mín": 0.10,
                "Tx_Gest_Var": 0.12,
            },
            {
                "Tp_Fundo": "Multimercado",
                "CNPJ_Fundo": "98.765.432/0001-10",
                "Nome_Fundo": "Fundo Horizonte Multimercado",
                "Razão_Social": "Fundo Horizonte Demonstração",
                "Situação": "Ativo",
                "Prazo_Liq_Fin": "D+1",
                "Exercício": "2025",
                "Admin": "Admin Demo S.A.",
                "Gestor": "Gestora Exemplo Ltda",
                "Auditor": "Auditoria Demo",
                "Custodiante": "Banco Demo S.A.",
                "Tx_Adm_Fixo": 0.12,
                "Tx_Adm_Mín": 0.04,
                "Tx_Adm_Var": 0.06,
                "Tx_Gest_Fixo": 0.18,
                "Tx_Gest_Mín": 0.08,
                "Tx_Gest_Var": 0.10,
            },
            {
                "Tp_Fundo": "FIDC",
                "CNPJ_Fundo": "11.222.333/0001-44",
                "Nome_Fundo": "FIDC Exemplo Recebíveis",
                "Razão_Social": "FIDC Exemplo Securitizadora",
                "Situação": "Em constituição",
                "Prazo_Liq_Fin": "D+3",
                "Exercício": "2025",
                "Admin": "Custódia Demo Ltda",
                "Gestor": "Gestora Exemplo Ltda",
                "Auditor": "Auditoria Demo",
                "Custodiante": "Banco Demo S.A.",
                "Tx_Adm_Fixo": 0.10,
                "Tx_Adm_Mín": 0.03,
                "Tx_Adm_Var": 0.05,
                "Tx_Gest_Fixo": 0.16,
                "Tx_Gest_Mín": 0.07,
                "Tx_Gest_Var": 0.09,
            },
        ]
    )


def _assembleias_payload():
    items_a = [
        {
            "FUNDO": "Fundo Aurora FIC FIM",
            "ADMINISTRADOR": "Admin Demo S.A.",
            "STATUS": "OPEN",
            "RESPONSÁVEL": "Ana Exemplo",
            "DATA REF.": "2025-03-01",
            "DATA PUBLICAÇÃO": "2025-03-05",
            "DATA LIMITE": "2025-03-20",
        },
        {
            "FUNDO": "Fundo Horizonte Multimercado",
            "ADMINISTRADOR": "Admin Demo S.A.",
            "STATUS": "VOTO ENVIADO",
            "RESPONSÁVEL": "Bruno Exemplo",
            "DATA REF.": "2025-02-15",
            "DATA PUBLICAÇÃO": "2025-02-18",
            "DATA LIMITE": "2025-03-10",
        },
    ]
    items_b = [
        {
            "FUNDO": "FIDC Exemplo Recebíveis",
            "ADMINISTRADOR": "Custódia Demo Ltda",
            "STATUS": "APROVADO",
            "RESPONSÁVEL": "Carla Exemplo",
            "DATA REF.": "2025-01-10",
            "DATA PUBLICAÇÃO": "2025-01-12",
            "DATA LIMITE": "2025-02-01",
        },
    ]
    return pd.DataFrame(
        [
            {"input_datetime": "2025-03-10 14:22:00", "payload_json": json.dumps(items_a, ensure_ascii=False)},
            {"input_datetime": "2025-02-28 09:15:00", "payload_json": json.dumps(items_b, ensure_ascii=False)},
        ]
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _disponibilidade_rows().to_excel(OUT / "disponibilidade_caixa_fundos.xlsx", index=False, engine="openpyxl")
    _fundos_rows().to_excel(OUT / "base_de_dados_fundos.xlsx", index=False, engine="openpyxl")
    _assembleias_payload().to_excel(OUT / "controle_assembleias.xlsx", index=False, engine="openpyxl")
    print(f"Arquivos gravados em {OUT}")


if __name__ == "__main__":
    main()
