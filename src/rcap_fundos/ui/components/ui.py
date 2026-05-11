import pandas as pd
import streamlit as st
from datetime import date
from pathlib import Path

from rcap_fundos.core.demo_io import is_demo_mode, read_demo_xlsx
from rcap_fundos.core.rcap_bd import sql_connect


def _sidebar_logo_path(project_root: Path) -> Path | None:
    img_dir = project_root / "imagens"
    if not img_dir.is_dir():
        return None
    for name in (
        "vertex_asset_logo_fundo_escuro.png",
        "vertex_asset_logo_fundo_claro.png",
    ):
        candidate = img_dir / name
        if candidate.is_file():
            return candidate
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        found = sorted(img_dir.glob(ext))
        if found:
            return found[0]
    return None


def sidebar_menu():
    with st.sidebar:
        project_root = Path(__file__).resolve().parents[4]
        logo_path = _sidebar_logo_path(project_root)
        if logo_path is not None:
            st.image(str(logo_path), use_container_width=True)

        if is_demo_mode():
            st.markdown(
                '<p class="sidebar-env-note">'
                "Base sintética: sem dados pessoais nem identificação de titulares (Lei 13.709/2018)."
                "</p>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-section'><strong>Navegação</strong></div>", unsafe_allow_html=True)

        paginas = {
            "Disponibilidade de caixa": "disponibilidade_caixa",
            "Assembleias": "controle_assembleias",
            "Cadastro de fundos": "dados_fundos",
            "Saldo em conta corrente": "controle_liquidacoes",
        }

        if "pagina_atual" not in st.session_state:
            st.session_state.pagina_atual = "disponibilidade_caixa"

        for nome, valor in paginas.items():
            button_type = "primary" if valor == st.session_state.pagina_atual else "secondary"
            if st.button(nome, key=valor, type=button_type):
                st.session_state.pagina_atual = valor
                st.rerun()

        pagina_atual = st.session_state.pagina_atual

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    return None, None, None, pagina_atual, None


def carregar_dados_unificados(data_selecionada: date):
    """Carrega disponibilidade de caixa (MySQL ou planilha local conforme configuração)."""
    if is_demo_mode():
        df_unificado = read_demo_xlsx("disponibilidade_caixa_fundos")
        if df_unificado.empty:
            st.warning("Sem dados de disponibilidade para exibir.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None
        df_unificado = df_unificado.copy()
        df_unificado["DATA_REFERENCIA"] = pd.to_datetime(df_unificado["DATA_REFERENCIA"])
        df_unificado = df_unificado.sort_values(["DATA_REFERENCIA", "FUNDO"])
        return df_unificado, pd.DataFrame(), pd.DataFrame(), data_selecionada

    conn = sql_connect(database="rcap")
    if conn is None:
        st.error("Conexão MySQL indisponível. Defina MYSQL_* no .env ou RCAP_DEMO=1.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None

    try:
        query = """
            SELECT 
                DATA_REFERENCIA,
                FUNDO,
                CNPJ,
                ADMINISTRADOR,
                SALDO_CC,
                APLICACOES_RF,
                AUDITORIA,
                AUDITORIA_PEND,
                TX_GESTAO,
                TX_GESTAO_PEND,
                TX_ADM,
                TX_ADM_PEND,
                TX_ESCRITURACAO,
                TX_ESCRITURACAO_PEND,
                TX_CUSTODIA,
                TX_CUSTODIA_PEND,
                BANCO_LIQ,
                BANCO_LIQ_PEND,
                TX_CVM,
                TX_CVM_PEND,
                TX_CETIP,
                TX_CETIP_PEND,
                TX_ANBIMA,
                TX_ANBIMA_PEND,
                OUTROS
            FROM rcap.disponibilidade_caixa_fundos
        """
        try:
            df_unificado = pd.read_sql(query, conn)
        except Exception:
            df_unificado = pd.DataFrame()

        if df_unificado is not None and not df_unificado.empty:
            df_unificado["DATA_REFERENCIA"] = pd.to_datetime(df_unificado["DATA_REFERENCIA"])
            df_unificado = df_unificado.sort_values(["DATA_REFERENCIA", "FUNDO"])
            return df_unificado, pd.DataFrame(), pd.DataFrame(), data_selecionada

        query_max = "SELECT MAX(DATA_REFERENCIA) as max_data FROM rcap.disponibilidade_caixa_fundos"
        df_max = pd.read_sql(query_max, conn)
        if not df_max.empty and pd.notna(df_max.loc[0, "max_data"]):
            data_mais_recente = pd.to_datetime(df_max.loc[0, "max_data"]).date()
            query_recente = query + f" WHERE DATE(DATA_REFERENCIA) = '{data_mais_recente}'"
            df_unificado = pd.read_sql(query_recente, conn)
            if df_unificado is not None and not df_unificado.empty:
                df_unificado["DATA_REFERENCIA"] = pd.to_datetime(df_unificado["DATA_REFERENCIA"])
                df_unificado = df_unificado.sort_values(["DATA_REFERENCIA", "FUNDO"])
                return df_unificado, pd.DataFrame(), pd.DataFrame(), data_mais_recente

        st.warning("Sem dados de disponibilidade na origem configurada.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None
    finally:
        if conn:
            conn.close()


def formatar_moeda(valor):
    if pd.isna(valor):
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


