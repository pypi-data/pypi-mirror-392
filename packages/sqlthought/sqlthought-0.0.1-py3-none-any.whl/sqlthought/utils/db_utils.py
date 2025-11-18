"""
Database helper utilities for SQL-of-Thought.
"""

import sqlite3
from .logger import logger


def extract_schema(db_path: str) -> str:
    """Extract table + column names from SQLite database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]

    schema = {}

    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        schema[t] = [row[1] for row in cur.fetchall()]

    conn.close()

    logger.info("Schema extracted.")
    return str(schema)


def execute_sql(sql: str, db_path: str):
    """Execute SQL on SQLite DB. Returns (success: bool, result OR error)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return True, rows
    except Exception as e:
        conn.close()
        return False, str(e)


__all__ = ["extract_schema", "execute_sql"]
