"""Leitura de planilhas locais quando RCAP_DEMO está definido."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _flag_demo(val: str | object) -> bool:
    if val is None or val == "":
        return False
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def is_demo_mode() -> bool:
    if _flag_demo(os.environ.get("RCAP_DEMO", "")):
        return True
    try:
        import streamlit as st  # noqa: PLC0415

        if hasattr(st, "secrets"):
            try:
                if _flag_demo(st.secrets["RCAP_DEMO"]):
                    return True
            except (KeyError, TypeError, AttributeError):
                pass
    except Exception:
        pass
    return False


def demo_data_dir() -> Path:
    return project_root() / "demo_data"


def read_demo_xlsx(stem: str, *, sheet: int | str = 0) -> pd.DataFrame:
    path = demo_data_dir() / f"{stem}.xlsx"
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
