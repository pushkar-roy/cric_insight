import sqlite3

DB_PATH = "ipl_stats.db"

def get_season_stats(player_name):
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
    runs_scored_by_year = dict(cursor.fetchall())
    
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(SUM(batsman_runs), 
            SUM(CASE WHEN extras_type IN ('wides', 'noballs', 'penalty') THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.bowler = ? AND d.inning <= 2
        GROUP BY year
    ''', (player_name,))
    runs_given_by_year = dict(cursor.fetchall())

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
    fours_by_year = dict(cursor.fetchall())

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
    sixes_by_year = dict(cursor.fetchall())

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
    got_out_stats = dict(cursor.fetchall())

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
    wickets_by_year = dict(cursor.fetchall())

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
    innings_as_batsman = dict(cursor.fetchall())

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
    innings_as_bowler = dict(cursor.fetchall())

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
    catches_by_year = dict(cursor.fetchall())

    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(Count(d.ball) - SUM(CASE WHEN d.extras_type = "wides" THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        where d.batter = ? and d.inning <=2
        GROUP BY Year
    ''', (player_name,))
    total_ball_faced = dict(cursor.fetchall())
    
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS year,
            COALESCE(Count(d.ball) - SUM(CASE WHEN d.extras_type = "wides" or extras_type = "noballs" THEN 1 ELSE 0 END), 0)
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        where d.bowler = ? and d.inning <=2
        GROUP BY Year
    ''', (player_name,))
    total_ball_thrown = dict(cursor.fetchall())
    
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
    hundreds = dict(cursor.fetchall())
    
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
    fifties = dict(cursor.fetchall())

    cursor.execute('''
        SELECT
            year, 
            COALESCE(COUNT(*), 0) AS dot_balls
        FROM (
            SELECT 
                strftime('%Y', m.date) AS year, 
                d.match_id,
                d.over,
                d.ball
            FROM deliveries d
            JOIN matches m ON d.match_id = m.id
            WHERE d.bowler = ? 
            AND d.inning <= 2
            AND d.batsman_runs = 0 
            AND (d.extras_type IS NULL OR d.extras_type NOT IN ('wides', 'noballs', 'penalty'))
    )
    GROUP BY year
    ''', (player_name,))
    dot_balls_by_year = dict(cursor.fetchall())



    conn.close()
    
    
    # Calculate Batting & Bowling Derived Stats

    # Initialize dictionaries
    batting_avg_by_year = {}
    batting_strike_rate_by_year = {}
    bowling_avg_by_year = {}
    bowling_strike_rate_by_year = {}
    economy_by_year = {}

    # Calculate batting averages and strike rates per season
    for year in runs_scored_by_year:
        runs = runs_scored_by_year.get(year, 0)
        outs = got_out_stats.get(year, 0)
        balls_faced = total_ball_faced.get(year, 0)

        # Batting Average = Runs Scored / Number of Times Out (Avoid divide by zero)
        batting_avg_by_year[year] = round(runs / outs, 2) if outs > 0 else None

        # Batting Strike Rate = (Runs Scored / Balls Faced) * 100 (Avoid divide by zero)
        batting_strike_rate_by_year[year] = round((runs / balls_faced) * 100, 2) if balls_faced > 0 else None

    # Calculate bowling averages, strike rates, and economy per season
    for year in runs_given_by_year:
        runs_given = runs_given_by_year.get(year, 0)
        wickets = wickets_by_year.get(year, 0)
        balls_bowled = total_ball_thrown.get(year, 0)

        # Bowling Average = Runs Given / Wickets Taken (Avoid divide by zero)
        bowling_avg_by_year[year] = round(runs_given / wickets, 2) if wickets > 0 else None

        # Bowling Strike Rate = Balls Bowled / Wickets Taken (Avoid divide by zero)
        bowling_strike_rate_by_year[year] = round(balls_bowled / wickets, 2) if wickets > 0 else None

        # Economy Rate = (Runs Given / Overs Bowled) (Avoid divide by zero)
        overs_bowled = balls_bowled / 6
        economy_by_year[year] = round(runs_given / overs_bowled, 2) if overs_bowled > 0 else None

    # Return all calculated values along with original stats
    return {
        "runs_scored_by_year": runs_scored_by_year,
        "runs_given_by_year": runs_given_by_year,
        "fours_by_year": fours_by_year,
        "sixes_by_year": sixes_by_year,
        "wickets_by_year": wickets_by_year,
        "catches_by_year": catches_by_year,
        "ball_thrown_by_year": total_ball_thrown,
        "hundreds_by_year": hundreds,
        "fifties_by_year": fifties,
        "dot_balls_by_year": dot_balls_by_year,
        "batting_avg_by_year": batting_avg_by_year,
        "batting_strike_rate_by_year": batting_strike_rate_by_year,
        "bowling_avg_by_year": bowling_avg_by_year,
        "bowling_strike_rate_by_year": bowling_strike_rate_by_year,
        "economy_by_year": economy_by_year
    }


