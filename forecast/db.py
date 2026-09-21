import sqlite3
conn = sqlite3.connect(":memory:")


conn.execute("""
    CREATE TABLE demo (
        home_team  TEXT NOT NULL,
        away_team  TEXT NOT NULL,
        home_goals INTEGER NOT NULL
    )
""")



conn.execute("INSERT INTO demo VALUES (?, ?, ?)", ("Arsenal", "Chelsea", 3))
conn.execute("INSERT INTO demo VALUES (?, ?, ?)", ("Liverpool", "Everton", 1))
conn.execute("INSERT INTO demo VALUES (?, ?, ?)", ("Arsenal", "Everton", 2))


conn.execute("SELECT home_team, home_goals FROM demo WHERE home_goals >= 2").fetchall()
conn.execute("SELECT home_team, SUM(home_goals) FROM demo GROUP BY home_team").fetchall()
conn.execute("SELECT AVG(home_goals) FROM demo").fetchone()
