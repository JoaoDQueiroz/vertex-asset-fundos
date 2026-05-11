import pandas as pd
import streamlit as st

from rcap_fundos.core.demo_io import is_demo_mode, read_demo_xlsx
from rcap_fundos.core.disponibilidade_calculo import COL_DESPESAS, enriquecer_disponibilidade
from rcap_fundos.core.kpi_janela import agregar_janela, agregar_janela_anterior, dias_por_periodo, pct_variacao
from rcap_fundos.core.rcap_bd import sql_connect
from rcap_fundos.ui.charts_caixa import fig_donut_fundos_por_administrador


def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return valor


def carregar_disponibilidade_caixa():
    if is_demo_mode():
        df = read_demo_xlsx("disponibilidade_caixa_fundos")
        if not df.empty and "DATA_REFERENCIA" in df.columns:
            df = df.copy()
            df["DATA_REFERENCIA"] = pd.to_datetime(df["DATA_REFERENCIA"])
        return df
    conn = sql_connect(database="rcap")
    if conn is None:
        st.error("Conexão MySQL indisponível. Defina MYSQL_* no .env ou RCAP_DEMO=1.")
        return pd.DataFrame()
    query = "SELECT * FROM disponibilidade_caixa_fundos"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def main(*_):
    st.title("Disponibilidade de caixa")
    df = carregar_disponibilidade_caixa()
    if df.empty:
        st.warning("Nenhum dado disponível na base consolidada.")
        st.stop()

    df_full = enriquecer_disponibilidade(df)
    col_despesas = COL_DESPESAS

    data_selecionada = None
    if "DATA_REFERENCIA" in df_full.columns:
        df_full["DATA_REFERENCIA"] = pd.to_datetime(df_full["DATA_REFERENCIA"])
        datas_disponiveis = sorted(df_full["DATA_REFERENCIA"].dt.date.unique())
        data_selecionada = st.date_input(
            "Data de referência",
            value=max(datas_disponiveis),
            min_value=min(datas_disponiveis),
            max_value=max(datas_disponiveis),
        )

    fundos_disponiveis = sorted(df_full["FUNDO"].unique())
    fundos_selecionados = st.multiselect("Fundos", options=fundos_disponiveis, default=fundos_disponiveis)
    fundos_filtro = fundos_selecionados if fundos_selecionados else None

    st.subheader("Indicadores")
    periodo = st.radio("Janela", ["1M", "3M", "6M"], horizontal=True)

    dias = dias_por_periodo(periodo)
    fim = pd.Timestamp(data_selecionada) if data_selecionada is not None else df_full["DATA_REFERENCIA"].max()
    cur = agregar_janela(df_full, fundos_filtro, fim, dias)
    prev = agregar_janela_anterior(df_full, fundos_filtro, fim, dias)
    v_pl = pct_variacao(cur["pl"], prev["pl"])
    v_cap = pct_variacao(cur["captacao"], prev["captacao"])
    v_cot = pct_variacao(float(cur["cotistas"]), float(prev["cotistas"])) if prev["cotistas"] else None

    col_esq, col_dir = st.columns([1.05, 0.95])
    with col_esq:
        r1a, r1b, r1c = st.columns(3)
        r1a.metric(
            "Patrimônio ref. (MM)",
            f"{cur['pl'] / 1e6:.2f}".replace(".", ","),
            delta=round(v_pl, 2) if v_pl is not None else None,
        )
        r1b.metric(
            "Captação líquida (janela)",
            formatar_moeda(cur["captacao"]),
            delta=round(v_cap, 2) if v_cap is not None else None,
        )
        r1c.metric(
            "Cotistas ativos (ref.)",
            cur["cotistas"],
            delta=round(v_cot, 2) if v_cot is not None else None,
        )
    with col_dir:
        ult = cur["ultimo_dia"]
        if ult is not None and "ADMINISTRADOR" in df_full.columns:
            slice_ult = df_full.loc[df_full["DATA_REFERENCIA"] == ult]
            if fundos_filtro:
                slice_ult = slice_ult.loc[slice_ult["FUNDO"].isin(fundos_filtro)]
            por_adm = slice_ult.groupby("ADMINISTRADOR")["FUNDO"].nunique().to_dict()
            st.plotly_chart(
                fig_donut_fundos_por_administrador(por_adm, "Fundos por administrador"),
                use_container_width=True,
            )

    if data_selecionada is not None:
        df = df_full.loc[df_full["DATA_REFERENCIA"].dt.date == data_selecionada].copy()
    else:
        df = df_full.copy()
    if fundos_selecionados:
        df = df.loc[df["FUNDO"].isin(fundos_selecionados)]

    abas = st.tabs(
        [
            "Relatório Geral",
            "Relatório Limpo (Sem PENDs)",
            "Despesas Geral Detalhado",
            "Despesas Limpo Detalhado",
            "Despesas PENDs Detalhado",
        ]
    )

    # --- Funções de estilo ---
    def colorir_valores(val):
        try:
            val = float(val)
            if val < 0:
                return "color: red;"
            elif val > 0:
                return "color: green;"
        except Exception:
            pass
        return ""

    def zebra_linhas(row):
        if row.name % 2 == 0:
            return ["background-color: #f5f5f5"] * len(row)
        else:
            return [""] * len(row)

    def destaque_total(row):
        if "FUNDO" in row and row["FUNDO"] == "TOTAL":
            return ["background-color: #f7f6f3; font-weight: bold"] * len(row)
        else:
            return [""] * len(row)

    def destaque_coluna_total(s):
        return [
            "background-color: #f7f6f3; font-weight: bold" if s.name in ["TOTAL_DESPESAS", "DISPONIBILIDADE"] else ""
            for _ in s
        ]

    styler_header = [{"selector": "th", "props": [("font-weight", "bold"), ("background-color", "#f5f5f5")]}]

    # --- Relatório Geral ---
    with abas[0]:
        st.subheader("Relatório Geral")
        colunas = ["FUNDO", "CNPJ", "ADMINISTRADOR", "SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"]
        df_rel = df[colunas].copy()
        total = df_rel[["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"]].sum()
        total_row = pd.DataFrame(
            {
                "FUNDO": ["TOTAL"],
                "CNPJ": [""],
                "ADMINISTRADOR": [""],
                "SALDO_CC": [total["SALDO_CC"]],
                "APLICACOES_RF": [total["APLICACOES_RF"]],
                "DESPESAS": [total["DESPESAS"]],
                "DISPONIBILIDADE": [total["DISPONIBILIDADE"]],
            }
        )
        df_rel = pd.concat([df_rel, total_row], ignore_index=True)
        linhas = min(len(df_rel), 13)
        altura = 38 + 35 * linhas
        st.dataframe(
            df_rel.style.format(formatar_moeda, subset=["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"])
            .applymap(colorir_valores, subset=["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"])
            .apply(zebra_linhas, axis=1)
            .apply(destaque_total, axis=1)
            .apply(destaque_coluna_total, axis=0)
            .set_table_styles(styler_header),
            use_container_width=True,
            height=altura,
        )

    # --- Relatório Limpo (Sem PENDs) ---
    with abas[1]:
        st.subheader("Relatório Limpo (Sem PENDs)")
        col_despesas_ok = [c for c in col_despesas if not c.endswith("_PEND") and c in df.columns]
        col_despesas_pend = [c for c in col_despesas if c.endswith("_PEND") and c in df.columns]
        df_limpo = df.copy()
        if "OUTROS" in df_limpo.columns and col_despesas_pend:
            mask_pend = df_limpo[col_despesas_pend].sum(axis=1) > 0
            df_limpo.loc[mask_pend, "OUTROS"] = 0
        df_limpo["DESPESAS_LIMPO"] = df_limpo[col_despesas_ok].sum(axis=1)
        df_limpo["DISPONIBILIDADE_LIMPO"] = df_limpo["SALDO_CC"] + df_limpo["APLICACOES_RF"] + df_limpo["DESPESAS_LIMPO"]
        colunas = ["FUNDO", "CNPJ", "ADMINISTRADOR", "SALDO_CC", "APLICACOES_RF", "DESPESAS_LIMPO", "DISPONIBILIDADE_LIMPO"]
        df_limpo = df_limpo[colunas].rename(columns={"DESPESAS_LIMPO": "DESPESAS", "DISPONIBILIDADE_LIMPO": "DISPONIBILIDADE"})
        total = df_limpo[["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"]].sum()
        total_row = pd.DataFrame(
            {
                "FUNDO": ["TOTAL"],
                "CNPJ": [""],
                "ADMINISTRADOR": [""],
                "SALDO_CC": [total["SALDO_CC"]],
                "APLICACOES_RF": [total["APLICACOES_RF"]],
                "DESPESAS": [total["DESPESAS"]],
                "DISPONIBILIDADE": [total["DISPONIBILIDADE"]],
            }
        )
        df_limpo = pd.concat([df_limpo, total_row], ignore_index=True)
        linhas = min(len(df_limpo), 13)
        altura = 38 + 35 * linhas
        st.dataframe(
            df_limpo.style.format(formatar_moeda, subset=["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"])
            .applymap(colorir_valores, subset=["SALDO_CC", "APLICACOES_RF", "DESPESAS", "DISPONIBILIDADE"])
            .apply(zebra_linhas, axis=1)
            .apply(destaque_total, axis=1)
            .apply(destaque_coluna_total, axis=0)
            .set_table_styles(styler_header),
            use_container_width=True,
            height=altura,
        )

    # --- Despesas Geral Detalhado ---
    with abas[2]:
        st.subheader("Despesas Geral Detalhado")
        col_desp_detail = [c for c in col_despesas if c in df.columns]
        df_detalhe = df[["FUNDO", "CNPJ", "ADMINISTRADOR"] + col_desp_detail].copy()
        df_detalhe["TOTAL_DESPESAS"] = df_detalhe[col_desp_detail].sum(axis=1)
        total = df_detalhe[col_desp_detail + ["TOTAL_DESPESAS"]].sum()
        total_row = pd.DataFrame(
            {
                "FUNDO": ["TOTAL"],
                "CNPJ": [""],
                "ADMINISTRADOR": [""],
                **{c: [total[c]] for c in col_desp_detail},
                "TOTAL_DESPESAS": [total["TOTAL_DESPESAS"]],
            }
        )
        df_detalhe = pd.concat([df_detalhe, total_row], ignore_index=True)
        linhas = min(len(df_detalhe), 13)
        altura = 38 + 35 * linhas
        st.dataframe(
            df_detalhe.style.format(formatar_moeda, subset=col_desp_detail + ["TOTAL_DESPESAS"])
            .applymap(colorir_valores, subset=col_desp_detail + ["TOTAL_DESPESAS"])
            .apply(zebra_linhas, axis=1)
            .apply(destaque_total, axis=1)
            .apply(destaque_coluna_total, axis=0)
            .set_table_styles(styler_header),
            use_container_width=True,
            height=altura,
        )

    # --- Despesas Limpo Detalhado ---
    with abas[3]:
        st.subheader("Despesas Limpo Detalhado")
        col_despesas_ok = [c for c in col_despesas if not c.endswith("_PEND") and c in df.columns]
        col_despesas_pend = [c for c in col_despesas if c.endswith("_PEND") and c in df.columns]
        df_limpo = df[["FUNDO", "CNPJ", "ADMINISTRADOR"] + col_despesas_ok].copy()
        if "OUTROS" in df_limpo.columns and col_despesas_pend:
            mask_pend = df[col_despesas_pend].sum(axis=1) > 0
            df_limpo.loc[mask_pend, "OUTROS"] = 0
        df_limpo["TOTAL_DESPESAS"] = df_limpo[col_despesas_ok].sum(axis=1)
        total = df_limpo[col_despesas_ok + ["TOTAL_DESPESAS"]].sum()
        total_row = pd.DataFrame(
            {
                "FUNDO": ["TOTAL"],
                "CNPJ": [""],
                "ADMINISTRADOR": [""],
                **{c: [total[c]] for c in col_despesas_ok},
                "TOTAL_DESPESAS": [total["TOTAL_DESPESAS"]],
            }
        )
        df_limpo = pd.concat([df_limpo, total_row], ignore_index=True)
        linhas = min(len(df_limpo), 13)
        altura = 38 + 35 * linhas
        st.dataframe(
            df_limpo.style.format(formatar_moeda, subset=col_despesas_ok + ["TOTAL_DESPESAS"])
            .applymap(colorir_valores, subset=col_despesas_ok + ["TOTAL_DESPESAS"])
            .apply(zebra_linhas, axis=1)
            .apply(destaque_total, axis=1)
            .apply(destaque_coluna_total, axis=0)
            .set_table_styles(styler_header),
            use_container_width=True,
            height=altura,
        )

    # --- Despesas PENDs Detalhado ---
    with abas[4]:
        st.subheader("Despesas PENDs Detalhado")
        col_despesas_pend = [c for c in col_despesas if c.endswith("_PEND") and c in df.columns]
        df_pend = df[["FUNDO", "CNPJ", "ADMINISTRADOR"] + col_despesas_pend].copy()
        df_pend["TOTAL_DESPESAS"] = df_pend[col_despesas_pend].sum(axis=1)
        total = df_pend[col_despesas_pend + ["TOTAL_DESPESAS"]].sum()
        total_row = pd.DataFrame(
            {
                "FUNDO": ["TOTAL"],
                "CNPJ": [""],
                "ADMINISTRADOR": [""],
                **{c: [total[c]] for c in col_despesas_pend},
                "TOTAL_DESPESAS": [total["TOTAL_DESPESAS"]],
            }
        )
        df_pend = pd.concat([df_pend, total_row], ignore_index=True)
        linhas = min(len(df_pend), 13)
        altura = 38 + 35 * linhas
        st.dataframe(
            df_pend.style.format(formatar_moeda, subset=col_despesas_pend + ["TOTAL_DESPESAS"])
            .applymap(colorir_valores, subset=col_despesas_pend + ["TOTAL_DESPESAS"])
            .apply(zebra_linhas, axis=1)
            .apply(destaque_total, axis=1)
            .apply(destaque_coluna_total, axis=0)
            .set_table_styles(styler_header),
            use_container_width=True,
            height=altura,
        )


if __name__ == "__main__":
    main()


