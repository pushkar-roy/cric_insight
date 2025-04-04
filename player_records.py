import sqlite3

def safe_div(numerator, denominator, multiplier=1):
    return (numerator / denominator) * multiplier if denominator != 0 else 0

DB_PATH = "ipl_stats.db"

def get_player_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            batter,
            SUM(batsman_runs) as runs
        FROM deliveries
        where inning <=2
        group by batter
        order by runs desc
        limit 3
    ''')
    most_runs = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batter,
            SUM(case when batsman_runs = 4 then 1 else 0 end) as fours
        FROM deliveries
        where inning <=2
        group by batter
        order by fours desc
        limit 3
    ''')
    most_fours = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batter,
            SUM(case when batsman_runs = 6 then 1 else 0 end) as sixes
        FROM deliveries
        where inning <=2
        group by batter
        order by sixes desc
        limit 3
    ''')
    most_sixes = cursor.fetchall()

    cursor.execute('''
        SELECT
            bowler,
            sum(case when dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") then 1 else 0 end) as wickets
        FROM deliveries
        where inning <=2
        group by bowler
        order by wickets desc
        limit 3
    ''')
    most_wickets = cursor.fetchall()

    cursor.execute('''
SELECT 
    fielder, 
    COUNT(*) AS catches
FROM (
    SELECT fielder FROM deliveries
    WHERE inning <= 2 AND dismissal_kind = 'caught'
    
    UNION ALL
    SELECT bowler as fielder FROM deliveries
    WHERE inning <= 2 AND dismissal_kind = 'caught and bowled'
) AS combined_data
GROUP BY fielder
ORDER BY catches DESC
LIMIT 3;

    ''')
    most_catches = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batter,
            SUM(batsman_runs) as runs
        FROM deliveries
        where inning <=2
        group by batter, match_id
        order by runs desc
        limit 3
    ''')
    most_runs_match = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            batter,
            SUM(batsman_runs) as runs
        FROM deliveries
        where inning <=2
        group by batter, match_id, over
        order by runs desc
        limit 3
    ''')
    most_runs_over = cursor.fetchall()

    cursor.execute('''
        SELECT
            bowler,
            sum(case when dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") then 1 else 0 end) as wickets
        FROM deliveries
        where inning <=2
        group by bowler, match_id
        order by wickets desc
        limit 3
    ''')
    most_wickets_match = cursor.fetchall()
    
    cursor.execute('''
        SELECT
            bowler,
            sum(case when dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") then 1 else 0 end) as wickets
        FROM deliveries
        where inning <=2
        group by bowler, match_id, over
        order by wickets desc
        limit 3
    ''')
    most_wickets_over = cursor.fetchall()

    conn.close()

    return {
        "most_runs": most_runs,
        "most_fours": most_fours,
        "most_sixes": most_sixes,
        "most_wickets": most_wickets,
        "most_catches": most_catches,
        "most_runs_match": most_runs_match,
        "most_runs_over": most_runs_over,
        "most_wickets_match": most_wickets_match,
        "most_wickets_over": most_wickets_over,
    }
    