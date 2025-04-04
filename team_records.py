import sqlite3

def safe_div(numerator, denominator, multiplier=1):
    return (numerator / denominator) * multiplier if denominator != 0 else 0

DB_PATH = "ipl_stats.db"

def get_team_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            batting_team,
            SUM(batsman_runs) as runs
        FROM deliveries
        where inning <=2
        group by batting_team
        order by runs desc
        limit 3
    ''')
    most_runs = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batting_team,
            SUM(case when batsman_runs = 4 then 1 else 0 end) as fours
        FROM deliveries
        where inning <=2
        group by batting_team
        order by fours desc
        limit 3
    ''')
    most_fours = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batting_team,
            SUM(case when batsman_runs = 6 then 1 else 0 end) as sixes
        FROM deliveries
        where inning <=2
        group by batting_team
        order by sixes desc
        limit 3
    ''')
    most_sixes = cursor.fetchall()

    cursor.execute('''
        SELECT
            bowling_team,
            sum(case when dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") then 1 else 0 end) as wickets
        FROM deliveries
        where inning <=2
        group by bowling_team
        order by wickets desc
        limit 3
    ''')
    most_wickets = cursor.fetchall()

    cursor.execute('''
SELECT 
    bowling_team, 
    COUNT(*) AS catches
FROM (
    SELECT bowling_team FROM deliveries
    WHERE inning <= 2 AND dismissal_kind = 'caught'
    
    UNION ALL
    SELECT bowling_team FROM deliveries
    WHERE inning <= 2 AND dismissal_kind = 'caught and bowled'
) AS combined_data
GROUP BY bowling_team
ORDER BY catches DESC
LIMIT 3;

    ''')
    most_catches = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batting_team,
            SUM(total_runs) as runs
        FROM deliveries
        where inning <=2
        group by batting_team, match_id
        order by runs desc
        limit 3
    ''')
    most_runs_match = cursor.fetchall()

    cursor.execute('''
        SELECT
            winner,
            count(id) as wins
        FROM matches
        group by winner
        order by wins desc
        limit 3
    ''')
    most_match_wins = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            winner,
            count(id) as finals_wins
        FROM matches
        WHERE match_type = 'Final'
        group by winner
        order by finals_wins desc
        limit 3
    ''')
    most_finals_wins = cursor.fetchall()

    cursor.execute('''
        SELECT
            team, count(*) as finals_played
        FROM (
            SELECT team1 as team FROM matches WHERE match_type = 'Final'
            UNION ALL
            SELECT team2 as team FROM matches WHERE match_type = 'Final'
        ) AS finals_teams
        GROUP BY team
        ORDER BY finals_played DESC
        LIMIT 3
    ''')
    most_finals_played = cursor.fetchall()

    conn.close()

    return {
        "most_runs": most_runs,
        "most_fours": most_fours,
        "most_sixes": most_sixes,
        "most_wickets": most_wickets,
        "most_catches": most_catches,
        "most_runs_match": most_runs_match,
        "most_match_wins": most_match_wins,
        "most_finals_wins": most_finals_wins,
        "most_finals_played": most_finals_played,
    }
