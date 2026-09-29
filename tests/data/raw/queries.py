import sqlite3
from pathlib import Path

def print_matches(rows):
    for row in rows:
        print(f"{row['Date']}: {row['HomeTeam']} - {row['AwayTeam']} {row['FTHG']} : {row['FTAG']}")

def most_home_goals(conn):
    query = """
        SELECT HomeTeam,
        SUM(FTHG) AS goals 
        FROM meccsek 
        GROUP BY HomeTeam 
        ORDER BY goals DESC 
        LIMIT 1
    """
    return conn.execute(query).fetchone()

def first_10_matches(conn):
    #Nem kell sorbarakni, mert dátum szerint van most a táblázat rendezve, nekünk ez most megfelel
    query = "SELECT Date, HomeTeam, AwayTeam, FTHG, FTAG FROM meccsek LIMIT 10"
    return conn.execute(query).fetchall()

def get_biggest_margin_matches(conn):
    query = """
        SELECT Date, HomeTeam, AwayTeam, FTHG, FTAG, ABS(FTHG - FTAG) AS Difference 
        FROM meccsek 
        WHERE ABS(FTHG - FTAG) = (
            SELECT MAX(ABS(FTHG - FTAG)) 
            FROM meccsek
        )
        ORDER BY Date DESC
    """
    return conn.execute(query).fetchall()

def full_time_result_count(conn):
    query = "SELECT FTR, COUNT(FTR) as Count FROM meccsek GROUP BY FTR"
    return conn.execute(query).fetchall()

def all_games_played_by_each_club(conn):
    query = """
    SELECT Team, COUNT(*) AS TotalGames
    FROM (SELECT HomeTeam AS Team
    FROM meccsek
    UNION ALL
    SELECT AwayTeam AS Team
    FROM meccsek)
    GROUP BY Team
    ORDER BY TotalGames DESC
    """
    return conn.execute(query).fetchall()


def game_status_by_engagement(conn):

    query = """
    SELECT HomeTeam, AwayTeam, FTHG, FTAG,
        CASE 
        WHEN ABS(FTHG - FTAG) = 0 THEN 'Döntetlen'
        WHEN ABS(FTHG - FTAG) = 1 THEN 'Szoros'
        WHEN ABS(FTHG - FTAG) BETWEEN 2 AND 3 THEN 'Egyértelmű'
        ELSE 'Gálajátszma'
        END as jatek_minosege
    FROM meccsek
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
        HomeTeam as csapat,
        1 as jatszott,
        
        CASE WHEN FTR='H' THEN 1 ELSE 0 END as gyozelem,
        CASE WHEN FTR='A' THEN 1 ELSE 0 END as vereseg,
        CASE WHEN FTR='D' THEN 1 ELSE 0 END as dontetlen,

        FTHG as lott,
        FTAG as kapott,
        CASE WHEN FTR='H' THEN 3
             WHEN FTR='D' THEN 1
             ELSE 0 END as pont
        FROM meccsek

        UNION ALL

        SELECT 
        AwayTeam as csapat,
        1 as jatszott,
        
        CASE WHEN FTR='A' THEN 1 ELSE 0 END as gyozelem,
        CASE WHEN FTR='H' THEN 1 ELSE 0 END as vereseg,
        CASE WHEN FTR='D' THEN 1 ELSE 0 END as dontetlen,

        FTAG as lott,
        FTHG as kapott,
        
        CASE WHEN FTR='H' THEN 0
            WHEN FTR='D' THEN 1
            ELSE 3 END as pont
        FROM meccsek)

        GROUP BY csapat
        ORDER BY pontok DESC, (lott - kapott) DESC, lott DESC

        """
    return conn.execute(query).fetchall()



with sqlite3.connect("foci.db") as conn:
    conn.row_factory = sqlite3.Row
    
    '''
    rows = conn.execute("SELECT * FROM meccsek WHERE HomeTeam = 'Arsenal'").fetchall()
    
    for row in rows:
        print(row["Date"], row["HomeTeam"], row["AwayTeam"], row['FTHG'], '-',row['FTAG'])

    rows = conn.execute("SELECT * FROM meccsek WHERE HomeTeam = 'Man City' OR AwayTeam = 'Man City'").fetchall()
    for row in rows:
        print(row["Date"], row["HomeTeam"], row["AwayTeam"], row['FTHG'], '-',row['FTAG'])

    

    print("--- Az első 10 meccs a ligában ---")
    first_10_matches = first_10_matches(conn)
    print_matches(first_10_matches)


    matches = full_time_result_count(conn)
    for row in matches:
        print(f"{row['FTR']} - {row['Count']}")

    matches = most_home_goals(conn)
    print(f"--- TEAM WITH THE MOST HOME GOALS: {matches['HomeTeam']}, having scored {matches['goals']} goals")
    
    matches = get_biggest_margin_matches(conn)
    print(f"--- LEGNAGYOBB GÓLKÜLÖNBSÉGŰ MECCSEK ({len(matches)} db) ---")
    for row in matches:
        print(f"{row['Date']} | {row['HomeTeam']} {row['FTHG']}-{row['FTAG']} {row['AwayTeam']} (Különbség: {row['Difference']})")

    matches = all_games_played_by_each_club(conn)
    print("--- We do not have all the games for this club: ---")
    for row in matches:
        if row["TotalGames"] != 38:
            print(f"{row["Team"]} played: {row["TotalGames"]} games")


    matches = game_status_by_engagement(conn)
    for row in matches:
        print(f"{row["HomeTeam"]} - {row["AwayTeam"]}, {row["FTHG"]}-{row["FTAG"]} {row["jatek_minosege"]}")
    '''


    matches = full_table(conn)

    header = f"{'Csapat':<20} | {'P':>3} | {'Gy':>2} | {'D':>2} | {'V':>2} | {'GK':>4} | {'Lőtt':>4} : {'Kapott':<4}"
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
