import sqlite3

DB_PATH = "ipl_stats.db"

def get_team_stats_by_season(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Season-wise total matches played
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            COUNT(m.id) AS total_matches
        FROM matches m
        WHERE m.team1 = ? OR m.team2 = ?
        GROUP BY season
        ORDER BY season
    ''', (team_name, team_name))
    matches_by_season = dict(cursor.fetchall())

    # Season-wise wins
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            COUNT(*) AS total_wins
        FROM matches m
        WHERE m.winner = ?
        GROUP BY season
        ORDER BY season
    ''', (team_name,))
    wins_by_season = dict(cursor.fetchall())

    # Season-wise losses
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            COUNT(*) AS total_losses
        FROM matches m
        WHERE (m.team1 = ? OR m.team2 = ?) AND (m.winner <> ? AND m.winner IS NOT NULL)
        GROUP BY season
        ORDER BY season
    ''', (team_name, team_name, team_name))
    losses_by_season = dict(cursor.fetchall())

    # Season-wise total runs, fours, and sixes
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            SUM(d.total_runs) AS total_runs
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batting_team = ? AND d.inning <= 2
        GROUP BY season
        ORDER BY season
    ''', (team_name,))
    runs_scored_by_season = dict(cursor.fetchall())

    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            SUM(CASE WHEN d.total_runs = 4 THEN 1 ELSE 0 END) AS total_fours
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batting_team = ? AND d.inning <= 2
        GROUP BY season
        ORDER BY season
    ''', (team_name,))
    fours_by_season = dict(cursor.fetchall())
    
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            SUM(CASE WHEN d.total_runs = 6 THEN 1 ELSE 0 END) AS total_sixes
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.batting_team = ? AND d.inning <= 2
        GROUP BY season
        ORDER BY season
    ''', (team_name,))
    sixes_by_season = dict(cursor.fetchall())

    # Season-wise total wickets
    cursor.execute('''
        SELECT 
            strftime('%Y', m.date) AS season,
            COUNT(*) AS total_wickets
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        WHERE d.bowling_team = ? AND d.inning <= 2 AND d.is_wicket = 1
        GROUP BY season
        ORDER BY season
    ''', (team_name,))
    wickets_by_season = dict(cursor.fetchall())

    conn.close()

    return {
        "total_matches": matches_by_season,
        "total_wins": wins_by_season,
        "total_losses": losses_by_season,
        "total_runs": runs_scored_by_season,
        "total_wickets": wickets_by_season,
        "total_fours": fours_by_season,
        "total_sixes": sixes_by_season,
    }

# Example usage
print(get_team_stats_by_season("Mumbai Indians"))
