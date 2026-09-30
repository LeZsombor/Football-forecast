import sqlite3
from pathlib import Path

# Útvonalak meghatározása a projekt gyökeréhez képest
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "forecast" else BASE_DIR
DB_PATH = PROJECT_ROOT / "data" / "foci.db"

if not DB_PATH.exists():
    raise FileNotFoundError(f"Nem található az adatbázis ezen az útvonalon: {DB_PATH}")


def print_matches(rows):
    for row in rows:
        print(f"{row['match_date']}: {row['home_team']} - {row['away_team']} " 
        f"{row['home_goals']} : {row['away_goals']}")


def most_home_goals(conn):
    query = """
        SELECT home_team, SUM(home_goals) AS goals 
        FROM matches 
        GROUP BY home_team 
        ORDER BY goals DESC 
        LIMIT 1
    """
    return conn.execute(query).fetchone()


def first_10_matches(conn):
    query = "SELECT match_date, home_team, away_team, home_goals,"
    " away_goals FROM matches LIMIT 10"
    return conn.execute(query).fetchall()


def get_biggest_margin_matches(conn):
    query = """
        SELECT match_date, home_team, away_team, home_goals, away_goals, 
        ABS(home_goals - away_goals) AS Difference 
        FROM matches 
        WHERE ABS(home_goals - away_goals) = (
            SELECT MAX(ABS(home_goals - away_goals)) 
            FROM matches
        )
        ORDER BY match_date DESC
    """
    return conn.execute(query).fetchall()


def full_time_result_count(conn):
    query = "SELECT result, COUNT(result) as Count FROM matches GROUP BY result"
    return conn.execute(query).fetchall()


def all_games_played_by_each_club(conn):
    query = """
    SELECT Team, COUNT(*) AS TotalGames
    FROM (
        SELECT home_team AS Team FROM matches
        UNION ALL
        SELECT away_team AS Team FROM matches
    )
    GROUP BY Team
    ORDER BY TotalGames DESC
    """
    return conn.execute(query).fetchall()


def game_status_by_engagement(conn):
    query = """
    SELECT home_team, away_team, home_goals, away_goals,
        CASE 
            WHEN ABS(home_goals - away_goals) = 0 THEN 'Döntetlen'
            WHEN ABS(home_goals - away_goals) = 1 THEN 'Szoros'
            WHEN ABS(home_goals - away_goals) BETWEEN 2 AND 3 THEN 'Egyértelmű'
            ELSE 'Gálajátszma'
        END as jatek_minosege
    FROM matches
    """
    return conn.execute(query).fetchall()


def full_table(conn):
    query = """
        SELECT
            csapat,
            SUM(jatszott) as jatszott,
            SUM(gyozelem) as gyozelem,
            SUM(dontetlen) as dontetlen,
            SUM(vereseg) as vereseg,
            SUM(lott) as lott,
            SUM(kapott) as kapott, 
            SUM(pont) as pontok
        FROM ( 
            SELECT 
                home_team as csapat,
                1 as jatszott,
                CASE WHEN result = 'H' THEN 1 ELSE 0 END as gyozelem,
                CASE WHEN result = 'A' THEN 1 ELSE 0 END as vereseg,
                CASE WHEN result = 'D' THEN 1 ELSE 0 END as dontetlen,
                home_goals as lott,
                away_goals as kapott,
                CASE 
                    WHEN result = 'H' THEN 3
                    WHEN result = 'D' THEN 1
                    ELSE 0 
                END as pont
            FROM matches

            UNION ALL

            SELECT 
                away_team as csapat,
                1 as jatszott,
                CASE WHEN result = 'A' THEN 1 ELSE 0 END as gyozelem,
                CASE WHEN result = 'H' THEN 1 ELSE 0 END as vereseg,
                CASE WHEN result = 'D' THEN 1 ELSE 0 END as dontetlen,
                away_goals as lott,
                home_goals as kapott,
                CASE 
                    WHEN result = 'A' THEN 3
                    WHEN result = 'D' THEN 1
                    ELSE 0 
                END as pont
            FROM matches
        )
        GROUP BY csapat
        ORDER BY pontok DESC, (lott - kapott) DESC, lott DESC
    """
    return conn.execute(query).fetchall()


def main():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        matches = full_table(conn)

        header = f"{'Csapat':<20} | {'P':>3} | {'Gy':>2} | {'D':>2} |"
        f" {'V':>2} | {'GK':>4} | {'Lőtt':>4} : {'Kapott':<4}"
        print(header)
        print("-" * len(header))
        for row in matches:
            goal_diff = row['lott'] - row['kapott']
            diff_str = f"+{goal_diff}" if goal_diff > 0 else str(goal_diff)

            print(
                f"{row['csapat']:<20} | "
                f"{row['pontok']:>3} | "
                f"{row['gyozelem']:>2} | "
                f"{row['dontetlen']:>2} | "
                f"{row['vereseg']:>2} | "
                f"{diff_str:>4} | "
                f"{row['lott']:>4} : {row['kapott']:<4}"
            )


if __name__ == "__main__":
    main()