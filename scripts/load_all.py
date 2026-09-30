import sqlite3
from pathlib import Path

from forecast.db import create_schema, load_csv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent




DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "foci.db"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


with sqlite3.connect(DB_PATH) as conn:
    create_schema(conn)
    
    for csv_file in RAW_DATA_DIR.glob("*.csv"):
        season = csv_file.stem
        n = load_csv(conn, csv_file, season)
        print(f"{csv_file.name}: {n} sor betöltve")