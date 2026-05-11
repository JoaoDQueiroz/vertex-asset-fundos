import json

import pandas as pd
import streamlit as st

from rcap_fundos.core.demo_io import is_demo_mode, read_demo_xlsx
from rcap_fundos.core.rcap_bd import sql_connect


def carregar_assembleias():
    if is_demo_mode():
        df = read_demo_xlsx("controle_assembleias")
    else:
        conn = sql_connect(database="rcap")
        if conn is None:
            st.error("Conexão MySQL indisponível. Defina MYSQL_* no .env ou RCAP_DEMO=1.")
            return pd.DataFrame()
        query = "SELECT input_datetime, payload_json FROM controle_assembleias"
        df = pd.read_sql(query, conn)
        conn.close()

    registros = []
    for _, row in df.iterrows():
        try:
            raw = row["payload_json"]
            payload = json.loads(raw if isinstance(raw, str) else str(raw))
            for item in payload:
                item["input_datetime"] = row["input_datetime"]
                registros.append(item)
        except Exception:
            continue

    return pd.DataFrame(registros) if registros else pd.DataFrame()


def main(*_):
    st.title("Assembleias")
    df = carregar_assembleias()
    if df.empty:
        st.info("Nenhum dado disponível para assembleias.")
        st.stop()

    for col in ["DATA REF.", "DATA PUBLICAÇÃO", "DATA LIMITE", "input_datetime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["DATA REF.", "DATA PUBLICAÇÃO", "DATA LIMITE"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d/%m/%Y")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fundos = sorted(df["FUNDO"].dropna().unique()) if "FUNDO" in df.columns else []
        fundo_sel = st.multiselect("Fundo", fundos, default=fundos)
    with col2:
        admins = sorted(df["ADMINISTRADOR"].dropna().unique()) if "ADMINISTRADOR" in df.columns else []
        admin_sel = st.multiselect("Administrador", admins, default=admins)
    with col3:
        status = sorted(df["STATUS"].dropna().unique()) if "STATUS" in df.columns else []
        status_sel = st.multiselect("Status", status, default=status)
    with col4:
        responsaveis = sorted(df["RESPONSÁVEL"].dropna().unique()) if "RESPONSÁVEL" in df.columns else []
        resp_sel = st.multiselect("Responsável", responsaveis, default=responsaveis)

    if fundo_sel and "FUNDO" in df.columns:
        df = df[df["FUNDO"].isin(fundo_sel)]
    if admin_sel and "ADMINISTRADOR" in df.columns:
        df = df[df["ADMINISTRADOR"].isin(admin_sel)]
    if status_sel and "STATUS" in df.columns:
        df = df[df["STATUS"].isin(status_sel)]
    if resp_sel and "RESPONSÁVEL" in df.columns:
        df = df[df["RESPONSÁVEL"].isin(resp_sel)]

    if "input_datetime" in df.columns:
        df = df.drop(columns=["input_datetime"])

    st.markdown("---")
    st.subheader("Assembleias e Eventos")

    if len(df) > 0:
        def zebra_linhas(row):
            return ["background-color: #f5f5f5" if row.name % 2 == 0 else "" for _ in row]

        def destaque_status(val):
            if isinstance(val, str):
                if "APROVADO" in val.upper():
                    return "background-color: #d4edda; color: #155724; font-weight: bold;"
                elif "VOTO ENVIADO" in val.upper():
                    return "background-color: #fff3cd; color: #856404; font-weight: bold;"
                elif "OPEN" in val.upper():
                    return "background-color: #cce5ff; color: #004085; font-weight: bold;"
            return ""

        st.dataframe(
            df.style.apply(zebra_linhas, axis=1).applymap(destaque_status, subset=["STATUS"] if "STATUS" in df.columns else None),
            use_container_width=True,
            height=min(38 + 35 * len(df), 800),
        )
    else:
        st.info("Nenhum registro encontrado com os filtros selecionados.")


if __name__ == "__main__":
    main()


