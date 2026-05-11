import pandas as pd
import streamlit as st

from rcap_fundos.core.demo_io import is_demo_mode, read_demo_xlsx
from rcap_fundos.core.rcap_bd import sql_connect


def carregar_dados_fundos():
    if is_demo_mode():
        return read_demo_xlsx("base_de_dados_fundos")
    conn = sql_connect(database="rcap")
    if conn is None:
        st.error("Conexão MySQL indisponível. Defina MYSQL_* no .env ou RCAP_DEMO=1.")
        return pd.DataFrame()
    query = "SELECT * FROM base_de_dados_fundos"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def main(*_):
    st.title("Cadastro de fundos")
    df = carregar_dados_fundos()
    if df.empty:
        st.info("Nenhum dado disponível na base de dados de fundos.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nomes = sorted(df["Nome_Fundo"].dropna().unique()) if "Nome_Fundo" in df.columns else []
        nome_sel = st.multiselect("Nome do Fundo", nomes, default=nomes)
    with col2:
        cnpjs = sorted(df["CNPJ_Fundo"].dropna().unique()) if "CNPJ_Fundo" in df.columns else []
        cnpj_sel = st.multiselect("CNPJ", cnpjs, default=cnpjs)
    with col3:
        admins = sorted(df["Admin"].dropna().unique()) if "Admin" in df.columns else []
        admin_sel = st.multiselect("Administrador", admins, default=admins)
    with col4:
        situacoes = sorted(df["Situação"].dropna().unique()) if "Situação" in df.columns else []
        situacao_sel = st.multiselect("Situação", situacoes, default=situacoes)

    if nome_sel and "Nome_Fundo" in df.columns:
        df = df[df["Nome_Fundo"].isin(nome_sel)]
    if cnpj_sel and "CNPJ_Fundo" in df.columns:
        df = df[df["CNPJ_Fundo"].isin(cnpj_sel)]
    if admin_sel and "Admin" in df.columns:
        df = df[df["Admin"].isin(admin_sel)]
    if situacao_sel and "Situação" in df.columns:
        df = df[df["Situação"].isin(situacao_sel)]

    abas = st.tabs(["Completa", "Taxas de Administração"])

    def zebra_linhas(row):
        return ["background-color: #f5f5f5" if row.name % 2 == 0 else "" for _ in row]

    with abas[0]:
        st.subheader("Tabela Completa")
        st.dataframe(df.style.apply(zebra_linhas, axis=1), use_container_width=True, height=min(38 + 35 * len(df), 800))

    with abas[1]:
        st.subheader("Taxas de Administração")
        cols_taxas = [
            "Nome_Fundo",
            "CNPJ_Fundo",
            "Admin",
            "Tx_Adm_Fixo",
            "Tx_Adm_Mín",
            "Tx_Adm_Var",
            "Tx_Gest_Fixo",
            "Tx_Gest_Mín",
            "Tx_Gest_Var",
        ]
        cols_taxas = [c for c in cols_taxas if c in df.columns]
        st.dataframe(df[cols_taxas].style.apply(zebra_linhas, axis=1), use_container_width=True, height=min(38 + 35 * len(df), 800))


if __name__ == "__main__":
    main()


