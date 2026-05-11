from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import streamlit as st

from rcap_fundos.ui.components.ui import sidebar_menu
from rcap_fundos.ui.screens import (
    controle_assembleias,
    controle_liquidacoes,
    dados_fundos,
    disponibilidade_caixa,
)
from rcap_fundos.ui.styles import load_css


st.set_page_config(
    page_title="Vertex Asset · Fundos",
    page_icon="📊",
    layout="wide",
)

load_css()

PAGINAS = {
    "disponibilidade_caixa": disponibilidade_caixa.main,
    "controle_assembleias": controle_assembleias.main,
    "dados_fundos": dados_fundos.main,
    "controle_liquidacoes": controle_liquidacoes.main,
}


def main() -> None:
    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "disponibilidade_caixa"

    _, _, _, pagina_atual, _ = sidebar_menu()
    st.session_state.pagina_atual = pagina_atual

    pagina = st.session_state.pagina_atual
    if pagina in PAGINAS:
        PAGINAS[pagina]()
    else:
        st.error(f"Página desconhecida: {pagina}")


if __name__ == "__main__":
    main()
