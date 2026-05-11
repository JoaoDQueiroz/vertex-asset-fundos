"""Cliente MySQL opcional (credenciais por variável de ambiente)."""

from __future__ import annotations

import os
import warnings

import pymysql
from dotenv import load_dotenv

warnings.filterwarnings("ignore")


def sql_connect(database: str = "rcap"):
    load_dotenv()
    host = os.environ.get("MYSQL_HOST", "").strip()
    user = os.environ.get("MYSQL_USER", "").strip()
    password = os.environ.get("MYSQL_PASSWORD", "").strip()
    if not host or not user or not password:
        return None
    try:
        return pymysql.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            ssl_verify_cert=False,
            ssl_verify_identity=False,
            connect_timeout=30,
        )
    except (pymysql.MySQLError, OSError, Exception):
        return None
