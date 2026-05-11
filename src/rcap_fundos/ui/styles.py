from pathlib import Path

import streamlit as st


def load_css() -> None:
    """
    Carrega o CSS global da aplicação.

    Usa um caminho robusto baseado na raiz do projeto, sem depender do diretório
    atual de execução.
    """
    project_root = Path(__file__).resolve().parents[3]
    css_path = project_root / "styles" / "styles.css"

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

