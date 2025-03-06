import sqlite3

DB_PATH = "ipl_stats.db"

def get_player_stats(player_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Career totals
    cursor.execute('''
        SELECT
            SUM(batsman_runs),
            SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END),
            SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END),
            SUM(CASE WHEN batsman_runs = 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN batsman_runs = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN batsman_runs = 2 THEN 1 ELSE 0 END),
            COUNT(CASE WHEN is_wicket = 1 THEN 1 ELSE NULL END)
        FROM deliveries
        WHERE batter = ?
    ''', (player_name,))
    (total_runs, total_fours, total_sixes, total_dots, total_singles, total_doubles, fall_wickets) = cursor.fetchone()

    # Season-wise totals
    cursor.execute('''
        SELECT 
            strftime('%Y', date),
            SUM(batsman_runs),
            SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END),
            SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END)
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE batter = ?
        GROUP BY strftime('%Y', date)
    ''', (player_name,))
    runs_per_season = cursor.fetchall()

    cursor.execute('''
        SELECT 
            AVG(total_runs),
            MAX(total_runs)
        FROM (
            SELECT 
                match_id,
                SUM(batsman_runs) AS total_runs
            FROM deliveries
            WHERE batter = ?
            GROUP BY match_id
        )
    ''', (player_name,))
    (avg_runs, highest_runs) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            AVG(total_wickets),
            MAX(total_wickets)
        FROM (
            SELECT 
                match_id,
                SUM(is_wicket) AS total_wickets
            FROM deliveries
            WHERE bowler = ?
            GROUP BY match_id
        )
    ''', (player_name,))
    (avg_wickets, highest_wickets) = cursor.fetchone()
    



    conn.close()

    return {
        "total_runs": total_runs,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "total_dots": total_dots,
        "total_singles": total_singles,
        "total_doubles": total_doubles,
        "got_out": fall_wickets,
        "runs_per_season": runs_per_season,
        "avg_runs": avg_runs,
        "highest_runs": highest_runs,
        "average_wickets": avg_wickets,
        "highest_wickets": highest_wickets,
    }
    
print(get_player_stats("V Kohli"))