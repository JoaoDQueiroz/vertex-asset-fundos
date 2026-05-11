import io

import pandas as pd
import streamlit as st

from rcap_fundos.core.demo_io import is_demo_mode, read_demo_xlsx
from rcap_fundos.core.rcap_bd import sql_connect


def carregar_saldos_duas_datas():
    if is_demo_mode():
        full = read_demo_xlsx("disponibilidade_caixa_fundos")
        if full.empty or "DATA_REFERENCIA" not in full.columns:
            return pd.DataFrame(), None, None
        full = full.copy()
        full["DATA_REFERENCIA"] = pd.to_datetime(full["DATA_REFERENCIA"])
        datas = sorted(full["DATA_REFERENCIA"].dropna().unique(), reverse=True)
        if len(datas) < 2:
            return pd.DataFrame(), None, None
        data_mais_recente, data_anterior = datas[0], datas[1]
        mask = full["DATA_REFERENCIA"].isin([data_mais_recente, data_anterior])
        df = full.loc[mask, ["FUNDO", "SALDO_CC", "DATA_REFERENCIA"]].copy()
        return df, data_mais_recente, data_anterior

    conn = sql_connect(database="rcap")
    if conn is None:
        st.error("Conexão MySQL indisponível. Defina MYSQL_* no .env ou RCAP_DEMO=1.")
        return pd.DataFrame(), None, None
    query_datas = """
        SELECT DISTINCT DATA_REFERENCIA FROM disponibilidade_caixa_fundos
        ORDER BY DATA_REFERENCIA DESC LIMIT 2
    """
    datas = pd.read_sql(query_datas, conn)["DATA_REFERENCIA"].sort_values(ascending=False).tolist()
    if len(datas) < 2:
        conn.close()
        return pd.DataFrame(), None, None

    data_mais_recente, data_anterior = datas[0], datas[1]
    query = f"""
        SELECT FUNDO, SALDO_CC, DATA_REFERENCIA
        FROM disponibilidade_caixa_fundos
        WHERE DATA_REFERENCIA IN ('{data_mais_recente}', '{data_anterior}')
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df, data_mais_recente, data_anterior


def main(*_):
    st.title("Saldo em conta corrente")
    df, data_mais_recente, data_anterior = carregar_saldos_duas_datas()
    if df.empty:
        st.info("Não há dados suficientes para comparar as datas.")
        st.stop()

    df_pivot = df.pivot(index="FUNDO", columns="DATA_REFERENCIA", values="SALDO_CC").reset_index()
    df_pivot["Diff"] = df_pivot[data_mais_recente] - df_pivot[data_anterior]
    df_diff = df_pivot.copy()

    col_mais_recente = pd.to_datetime(data_mais_recente).strftime("%d/%m/%Y")
    col_anterior = pd.to_datetime(data_anterior).strftime("%d/%m/%Y")
    df_diff = df_diff.rename(
        columns={
            data_mais_recente: f"Saldo {col_mais_recente}",
            data_anterior: f"Saldo {col_anterior}",
            "Diff": "Diferença",
        }
    )

    def zebra_linhas(row):
        return ["background-color: #f5f5f5" if row.name % 2 == 0 else "" for _ in row]

    def formatar_moeda(valor):
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return valor

    def colorir_diff(val):
        try:
            val = float(str(val).replace("R$", "").replace(".", "").replace(",", "."))
            if val > 0:
                return "color: green; font-weight: bold;"
            elif val < 0:
                return "color: red; font-weight: bold;"
        except Exception:
            pass
        return ""

    col_saldos = [c for c in df_diff.columns if c.startswith("Saldo")]
    col_diff = [c for c in df_diff.columns if "Diferença" in c]

    st.dataframe(
        df_diff.style.apply(zebra_linhas, axis=1)
        .format(formatar_moeda, subset=col_saldos + col_diff)
        .map(colorir_diff, subset=col_diff),
        use_container_width=True,
        height=min(38 + 35 * len(df_diff), 800),
    )

    if not df_diff.empty:
        output = io.BytesIO()
        df_diff.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        st.download_button(
            label="Baixar relatório em Excel (.xlsx)",
            data=output,
            file_name="controle_liquidacoes_diaria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    if df_diff.empty:
        st.info("Nenhuma movimentação detectada entre os dois dias.")


if __name__ == "__main__":
    main()


