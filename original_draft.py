import sqlite3

def safe_div(numerator, denominator, multiplier=1):
    return (numerator / denominator) * multiplier if denominator != 0 else 0

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
            SUM(CASE WHEN batsman_runs = 2 THEN 1 ELSE 0 END)
        FROM deliveries
        WHERE batter = ? and inning <=2
    ''', (player_name,))
    (total_runs_scored, total_fours, total_sixes, total_dots, total_singles, total_doubles) = cursor.fetchone()

    cursor.execute('''
        SELECT
            COUNT(ball)
        FROM deliveries
        WHERE player_dismissed = ? and inning <=2
    ''', (player_name,))
    (got_out,) = cursor.fetchone()

    cursor.execute('''
        SELECT
            SUM(batsman_runs),
            SUM(Case when extras_type  in ("wides", "noballs") then extra_runs else 0 end),
            sum(case when dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") then 1 else 0 end)
        FROM deliveries
        WHERE bowler = ? and inning <=2
    ''', (player_name,))
    (a, b, total_wickets_taken) = cursor.fetchone()
    total_runs_given = a+b
    
    cursor.execute('''
        SELECT
            COUNT(Distinct match_id)
        FROM deliveries
        WHERE batter = ? or non_striker = ?
    ''', (player_name, player_name))
    (total_innings_as_batsman,) = cursor.fetchone()
    
    cursor.execute('''
        SELECT
            COUNT(Distinct match_id)
        FROM deliveries
        WHERE bowler = ?
    ''', (player_name,))
    (total_innings_as_bowler,) = cursor.fetchone()
    
    cursor.execute('''
        SELECT
            COUNT()
        FROM deliveries
        WHERE (dismissal_kind = "caught" AND fielder = ?) or (dismissal_kind = "caught and bowled" AND bowler = ?)
    ''', (player_name, player_name))
    (total_catches,) = cursor.fetchone()

    cursor.execute('''
        SELECT 
            Count(ball),
            SUM(CASE WHEN extras_type = "wides" THEN 1 ELSE 0 END),
            SUM(CASE WHEN extras_type = "noballs" THEN 1 ELSE 0 END)
        FROM deliveries
        where batter = ? and inning <=2
    ''', (player_name,))
    (total_ball_faced, wide_ball_faced, noball_faced) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            Count(ball),
            SUM(CASE WHEN extras_type = "wides" or extras_type = "noballs" THEN 1 ELSE 0 END)
        FROM deliveries
        where bowler = ? and inning <=2
    ''', (player_name,))
    (total_ball_thrown, extra_ball_thrown) = cursor.fetchone()
    
    cursor.execute('''
        SELECT
            MAX(total_wicket), 
            SUM(case when total_wicket>=5 then 1 else 0 end),
            SUM(case when total_wicket>=3 then 1 else 0 end)
        from(
            select match_id, sum(is_wicket) as total_wicket
            from deliveries
            where bowler = ? and inning <=2 and dismissal_kind in ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket")
            group by match_id
        )
    ''', (player_name,))
    (high_wicket, five_wickets, three_wickets) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            MAX(total_runs),
            SUM(case when total_runs>=100 then 1 else 0 end),
            SUM(case when total_runs>=50 then 1 else 0 end)
        from(
            select match_id, sum(batsman_runs) as total_runs
            from deliveries
            where batter = ? and inning <=2
            group by match_id
        )
    ''', (player_name,))
    (high_score, hundreds, fifties) = cursor.fetchone()

    cursor.execute('''
SELECT 
    total_wicket || "/" || total_runs
FROM (
    SELECT 
        match_id,
        SUM(CASE WHEN dismissal_kind IN ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") THEN 1 ELSE 0 END) AS total_wicket,
        SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ("wides", "noballs") THEN extra_runs ELSE 0 END) AS total_runs
    FROM deliveries
    WHERE bowler = ? AND inning <= 2
    GROUP BY match_id
)
WHERE total_wicket = ?
ORDER BY total_runs
LIMIT 1;

    ''', (player_name, high_wicket))
    (best_figure, ) = cursor.fetchone()
    

    conn.close()

    return {
        "total_innings_as_batsman": total_innings_as_batsman,
        "total_innings_as_bowler": total_innings_as_bowler,
        "total_runs_scored": total_runs_scored,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "total_dots": total_dots,
        "total_singles": total_singles,
        "total_doubles": total_doubles,
        "total_catches": total_catches,
        "got_out": got_out,
        "total_ball_faced":total_ball_faced,
        "wide_ball_faced":wide_ball_faced,
        "noball_faced":noball_faced,
        "total_ball_thrown":total_ball_thrown,
        "extra_ball_thrown":extra_ball_thrown,
        "total_runs_given":total_runs_given,
        "total_wickets_taken":total_wickets_taken,
        "batting_strike_rate": (total_runs_scored/(total_ball_faced-wide_ball_faced))*100,
        "batting_avg": total_runs_scored/got_out,
        "bowling_avg": total_runs_given/total_wickets_taken,
        "bowling_strike_rate": (total_ball_thrown - extra_ball_thrown)/total_wickets_taken,
        "economy": (total_runs_given)/((total_ball_thrown-extra_ball_thrown)/6),
        "five_wickets": five_wickets,
        "three_wickets": three_wickets-five_wickets,
        "hundreds": hundreds,
        "fifties":fifties-hundreds,
        "high_score": high_score,
        "high_wicket": high_wicket,
        "best_figure": best_figure,
    }
    
print(get_player_stats("B Kumar"))