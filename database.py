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
    (total_runs, total_fours, total_sixes, total_dots, total_singles, total_doubles, total_wickets) = cursor.fetchone()

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

    # Aggregates
    cursor.execute('''
        SELECT 
            AVG(batsman_runs),
            MAX(batsman_runs),
            (SELECT COUNT(*) FROM deliveries WHERE bowler = ? AND is_wicket = 1)
        FROM deliveries
        WHERE batter = ?
    ''', (player_name, player_name))
    (avg_runs, highest_runs, highest_wickets) = cursor.fetchone()

    conn.close()

    return {
        "total_runs": total_runs,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "total_dots": total_dots,
        "total_singles": total_singles,
        "total_doubles": total_doubles,
        "total_wickets": total_wickets,
        "runs_per_season": runs_per_season,
        "avg_runs": avg_runs,
        "highest_runs": highest_runs,
        "highest_wickets": highest_wickets
    }

def get_team_stats(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Career totals
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN winner = ? THEN 1 ELSE NULL END),
            COUNT(CASE WHEN team1 = ? OR team2 = ? THEN 1 ELSE NULL END),
            SUM(total_runs)
        FROM matches
        JOIN deliveries ON matches.id = deliveries.match_id
        WHERE batting_team = ?
    ''', (team_name, team_name, team_name, team_name))
    (total_wins, total_matches, total_runs) = cursor.fetchone()

    # Season-wise totals
    cursor.execute('''
        SELECT 
            season,
            COUNT(CASE WHEN winner = ? THEN 1 ELSE NULL END),
            SUM(total_runs)
        FROM matches
        JOIN deliveries ON matches.id = deliveries.match_id
        WHERE batting_team = ?
        GROUP BY season
    ''', (team_name, team_name))
    stats_per_season = cursor.fetchall()

    # Aggregates
    cursor.execute('''
        SELECT 
            AVG(total_runs),
            MAX(total_runs)
        FROM matches
        JOIN deliveries ON matches.id = deliveries.match_id
        WHERE batting_team = ?
    ''', (team_name,))
    (avg_runs_per_match, highest_runs) = cursor.fetchone()

    conn.close()

    return {
        "total_wins": total_wins,
        "total_matches": total_matches,
        "total_runs": total_runs,
        "stats_per_season": stats_per_season,
        "avg_runs_per_match": avg_runs_per_match,
        "highest_runs": highest_runs
    }
