from __future__ import annotations

import sqlite3
from pathlib import Path


def create_connection(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str | Path) -> None:
    schema_path = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    ddl = schema_path.read_text(encoding="utf-8")
    with create_connection(db_path) as conn:
        conn.executescript(ddl)

