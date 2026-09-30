import csv
import sqlite3
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = {"Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"}


def create_schema(conn: sqlite3.Connection) -> None:
    query = """
    CREATE TABLE IF NOT EXISTS matches(
        id      INTEGER    PRIMARY KEY,
        season      TEXT    NOT NULL,
        match_date  TEXT    NOT NULL,
        home_team   TEXT    NOT NULL,
        away_team   TEXT    NOT NULL,
        home_goals  INTEGER NOT NULL CHECK (home_goals >= 0),
        away_goals  INTEGER NOT NULL CHECK (away_goals >= 0),
        result      TEXT    NOT NULL CHECK (result IN ('H', 'D', 'A')),
        UNIQUE (match_date, home_team, away_team)
        )
    """
    
    conn.execute(query)


def parse_date(input_date:str) -> str:
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(input_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"Nem sikerült értelmezni a dátumot: {input_date}")


def load_csv(conn: sqlite3.Connection, csv_path:Path, season_name:str) -> int:

    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")


    with open(csv_path, encoding = "utf-8") as f:
        reader = csv.DictReader(f)

        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or []):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            raise ValueError(f"Not all of the required field names were found. Missing: {missing}")

        records = []
        for row in reader:
            
            if not row["Date"] or not row["HomeTeam"]:
                continue

            records.append((
                season_name,
                parse_date(row.get("Date")),
                row["HomeTeam"],
                row["AwayTeam"],
                int(row["FTHG"]),
                int(row["FTAG"]),
                row["FTR"]
            )) 

    insert_query = """
    INSERT OR IGNORE INTO matches (
        season, match_date, home_team, away_team, home_goals, away_goals, result
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor = conn.executemany(insert_query, records)
    conn.commit()
    return cursor.rowcount
    