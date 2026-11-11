"""SQLite warehouse loader and SQL view runner."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from keystone.generate import Book

sqlite3.register_adapter(np.int64, int)
sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.float64, float)
sqlite3.register_adapter(np.float32, float)

VIEWS = (
    "vw_fence_scorecard",
    "vw_ab_test_member_web",
    "vw_daily_funnel",
    "vw_lead_time_response",
    "vw_hotel_rank",
)


def load(book: Book, db_path: Path, sql_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    sql_folder = sql_dir if sql_dir is not None else Path(__file__).resolve().parents[1] / "sql"
    scripts = sorted(sql_folder.glob("*.sql"))
    if not scripts:
        raise FileNotFoundError(f"No SQL files found in {sql_folder}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        book.sessions.to_sql("fact_sessions", conn, if_exists="replace", index=False)
        book.hotels.to_sql("dim_hotel", conn, if_exists="replace", index=False)
        book.fences.to_sql("dim_fence", conn, if_exists="replace", index=False)
        for script in scripts:
            conn.executescript(script.read_text(encoding="utf-8"))
        return {name: pd.read_sql_query(f"SELECT * FROM {name}", conn) for name in VIEWS}
