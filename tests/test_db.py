import sqlite3
from pathlib import Path

import pytest

from forecast.db import create_schema, load_csv, parse_date

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "tests" else BASE_DIR
SAMPLE_CSV = BASE_DIR / "data" / "sample.csv"


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    yield conn
    conn.close()


def test_db_parse_date():
    assert parse_date("30/09/2026") == "2026-09-30"
    assert parse_date("30/09/26") == "2026-09-30"


def test_load_csv_idempotency(db_conn):
    """Ellenőrzi, hogy többszöri CSV betöltés
     esetén sem duplázódnak a rekordok (INSERT OR IGNORE)."""
    season_name = "2025_26"

    # 1. Első betöltés
    first_loaded = load_csv(db_conn, SAMPLE_CSV, season_name)
    count_after_first = db_conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

    assert first_loaded > 0
    assert count_after_first == first_loaded

    # 2. Második betöltés ugyanazzal a fájllal
    second_loaded = load_csv(db_conn, SAMPLE_CSV, season_name)
    count_after_second = db_conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    assert second_loaded == 0

    # Az adatbázisban lévő sorok száma nem változhatott
    assert count_after_second == count_after_first

def test_data_consistency(db_conn):
    """Ellenőrzi, hogy az eredmény nem mond ellent a gólszámoknak."""
    load_csv(db_conn, SAMPLE_CSV, "2025_26")
    
    bad_rows = db_conn.execute("""
        SELECT COUNT(*) FROM matches
        WHERE (result = 'H' AND home_goals <= away_goals)
           OR (result = 'A' AND away_goals <= home_goals)
           OR (result = 'D' AND home_goals != away_goals)
    """).fetchone()[0]
    
    assert bad_rows == 0