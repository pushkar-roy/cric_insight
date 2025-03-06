import sqlite3

DB_PATH = "ipl_stats.db"

def get_player_stats(player_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            strftime('%Y', date),
            SUM(batsman_runs),
            SUM(CASE When extra_runs = 5 and extras_type in( "wides", "noballs") then 4 else 0 end),
            SUM(Case when extras_type in ("wides", "noballs") then 1 else 0 end)
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE bowler = ?
        Group by strftime('%Y', date)
    ''', (player_name,))
    total_runs_given = cursor.fetchall()

    cursor.execute('''
        SELECT
            strftime('%Y', date),
            COUNT(ball),
            Sum(Case when extras_type in ("wides", "noballs") then 1 else 0 end)
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE bowler = ?
        Group by strftime('%Y', date)
    ''', (player_name,))
    second = cursor.fetchall()

    # cursor.execute('''
    #     SELECT 
    #         strftime('%Y', date),
    #         SUM(runs),
    #         SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END),
    #         SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END)
    #     FROM deliveries
    #     JOIN matches ON deliveries.match_id = matches.id
    #     WHERE batter = ?
    #     GROUP BY strftime('%Y', date)
    # ''', (player_name,))
    # per_season = cursor.fetchall()

    conn.close()

    return {
        "total_catches": total_runs_given,
        "second":second,
        # "third":third,
        # "fourth":fourth,
        # "fifth":fifth

    }
    
print(get_player_stats("Arshdeep Singh"))