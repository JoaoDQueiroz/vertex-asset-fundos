"""Leitura de planilhas locais quando RCAP_DEMO está definido."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def is_demo_mode() -> bool:
    v = os.environ.get("RCAP_DEMO", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def demo_data_dir() -> Path:
    return project_root() / "demo_data"


def read_demo_xlsx(stem: str, *, sheet: int | str = 0) -> pd.DataFrame:
    path = demo_data_dir() / f"{stem}.xlsx"
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
