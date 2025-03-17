import sqlite3

DB_PATH = "ipl_stats.db"

def get_player_stats(player_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Year-wise runs
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(SUM(batsman_runs), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    runs_by_year = cursor.fetchall()

    # Year-wise 4s
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    fours_by_year = cursor.fetchall()

    # Year-wise 6s
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    sixes_by_year = cursor.fetchall()

    # Year-wise times got out
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(COUNT(ball), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.player_dismissed = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    got_out_stats = cursor.fetchall()

    # Year-wise wickets taken
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(SUM(CASE WHEN dismissal_kind IN ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.bowler = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    wickets_by_year = cursor.fetchall()

    # Year-wise innings as batsman
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(COUNT(DISTINCT d.match_id), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? OR d.non_striker = ?
        GROUP BY year
    ''', (player_name, player_name))
    innings_as_batsman = cursor.fetchall()

    # Year-wise innings as bowler
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(COUNT(DISTINCT d.match_id), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.bowler = ?
        GROUP BY year
    ''', (player_name,))
    innings_as_bowler = cursor.fetchall()

    # Year-wise catches
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(COUNT(*), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE (d.dismissal_kind = "caught" AND d.fielder = ?) OR (d.dismissal_kind = "caught and bowled" AND d.bowler = ?)
        GROUP BY year
    ''', (player_name, player_name))
    catches_by_year = cursor.fetchall()

    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(Count(d.ball) - SUM(CASE WHEN d.extras_type = "wides" THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        where d.batter = ? and d.inning <=2
        GROUP BY Year
    ''', (player_name,))
    total_ball_faced = cursor.fetchall()
    
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(Count(d.ball) - SUM(CASE WHEN d.extras_type = "wides" or extras_type = "noballs" THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        where d.bowler = ? and d.inning <=2
        GROUP BY Year
    ''', (player_name,))
    total_ball_thrown = cursor.fetchall()
    
    cursor.execute('''
    SELECT 
        year,
        COALESCE(SUM(CASE WHEN total_runs >= 100 THEN 1 ELSE 0 END), 0) AS hundreds
    FROM (
        SELECT strftime('%Y', m.date) AS year, d.match_id, SUM(batsman_runs) AS total_runs
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? AND d.inning <= 2
        GROUP BY year, d.match_id
    )
    GROUP BY year
    ''', (player_name,))
    hundreds = cursor.fetchall()
    
    cursor.execute('''
    SELECT 
        year,
        COALESCE(SUM(CASE WHEN total_runs >= 50 and total_runs<100 THEN 1 ELSE 0 END), 0) AS hundreds
    FROM (
        SELECT strftime('%Y', m.date) AS year, d.match_id, SUM(batsman_runs) AS total_runs
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batter = ? AND d.inning <= 2
        GROUP BY year, d.match_id
    )
    GROUP BY year
    ''', (player_name,))
    fifties = cursor.fetchall()

    cursor.execute('''
    SELECT
        year, 
        COALESCE(SUM(CASE WHEN batsman_runs <= 0 AND extra_runs <= 0 THEN 1 ELSE 0 END), 0) AS maiden_overs
    FROM (
        SELECT 
            strftime('%Y', m.date) AS year, 
            d.match_id,
            d.over,
            SUM(d.batsman_runs) AS batsman_runs,
            SUM(CASE WHEN d.extras_type IN ('wides', 'noballs', 'penalty') THEN 1 ELSE 0 END) AS extra_runs
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.bowler = ? AND d.inning <= 2
        GROUP BY d.match_id, d.over
    )
    GROUP BY year
    ''', (player_name,))
    maiden_overs = cursor.fetchall()

    conn.close()

    return {
        "runs_by_year": runs_by_year,
        "fours_by_year": fours_by_year,
        "sixes_by_year": sixes_by_year,
        "got_out_stats": got_out_stats,
        "wickets_by_year": wickets_by_year,
        "innings_as_batsman": innings_as_batsman,
        "innings_as_bowler": innings_as_bowler,
        "catches_by_year": catches_by_year,
        "ball_faced_by_year":total_ball_faced,
        "ball_thrown_by_year":total_ball_thrown,
        "hundreds_by_year":hundreds,
        "fifties_by_year":fifties,
        "maiden_by_year":maiden_overs
    }

print(get_player_stats("B Kumar"))
