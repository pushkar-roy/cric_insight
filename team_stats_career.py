import sqlite3

def safe_div(numerator, denominator, multiplier=1):
    return (numerator / denominator) * multiplier if denominator != 0 else 0

DB_PATH = "ipl_stats.db"

def get_player_stats(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Career totals
    
    cursor.execute('''
        SELECT 
            count(id)
        FROM
            matches
        WHERE
            team1 = ? or team2 = ?
            
    ''', (team_name, team_name))
    (total_match_played, ) = cursor.fetchone()

    cursor.execute('''
        SELECT 
            SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END),
            SUM(CASE WHEN toss_winner = ? THEN 1 ELSE 0 END)
        FROM
            matches
            
    ''', (team_name, team_name))
    (total_match_wins, total_toss_wins) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            SUM(total_runs),
            SUM(CASE WHEN total_runs = 4 THEN 1 ELSE 0 END),
            SUM(CASE WHEN total_runs = 6 THEN 1 ELSE 0 END)
        FROM
            deliveries
        WHERE
            batting_team = ? and inning <= 2
    ''', (team_name,))
    (total_runs, total_fours, total_sixes) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            COUNT(*)
        FROM
            deliveries
        WHERE
            bowling_team = ? and inning <= 2 and is_wicket = 1
    ''', (team_name,))
    (total_wickets, ) = cursor.fetchone()

    cursor.execute('''
        SELECT 
            total_runs, bowling_team
        FROM(
            SELECT 
                SUM(total_runs) as total_runs, bowling_team
            FROM
                deliveries
            WHERE
                batting_team = ? and inning <= 2
            GROUP BY
                match_id
        )     
        order by total_runs desc
        limit 1
    ''', (team_name,))
    (highest_score, highest_score_against) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            total_runs, bowling_team
        FROM (
            SELECT 
                SUM(total_runs) AS total_runs, bowling_team, COUNT(DISTINCT over) AS overs_bowled, SUM(CASE WHEN is_wicket = 1 THEN 1 ELSE 0 END) AS wickets
            FROM
                deliveries
            JOIN matches ON deliveries.match_id = matches.id
            WHERE
                batting_team = ? AND inning <= 2 AND matches.result <> 'no result'
            GROUP BY
                match_id
            HAVING
                overs_bowled >= 19 OR wickets = 10
        )
        ORDER BY total_runs ASC
        LIMIT 1
    ''', (team_name,))

    (lowest_score, lowest_score_against) = cursor.fetchone()


    cursor.execute('''
        SELECT 
            case when team1 = ? then team2 else team1 end as team,
            count(*) as total_wins
        FROM
            matches
        WHERE
            winner = ?
        GROUP BY team
        order by total_wins desc
        limit 1
    ''', (team_name, team_name,))
    (most_win_against_team, total_win_against_that_team) = cursor.fetchone()

    cursor.execute('''
        SELECT 
            case when team1 = ? then team2 else team1 end as team,
            count(*) as total_wins
        FROM
            matches
        WHERE
            (team1 = ? or team2 = ?) and (winner <> ? and winner <> 'None')
        GROUP BY team
        order by total_wins desc
        limit 1
    ''', (team_name, team_name, team_name, team_name))
    (most_lost_against_team, total_lost_against_that_team) = cursor.fetchone()

    cursor.execute('''
        SELECT 
            venue,
            count(*) as total_wins
        FROM
            matches
        WHERE
            winner = ?
        GROUP BY venue
        order by total_wins desc
        limit 1
    ''', (team_name,))
    (most_win_on_venue, total_win_on_that_venue) = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            venue,
            count(*) as total_wins
        FROM
            matches
        WHERE
            (team1 = ? or team2 = ?) and (winner <> ? and winner <> 'None')
        GROUP BY venue
        order by total_wins desc
        limit 1
    ''', (team_name, team_name, team_name))
    (most_lost_on_venue, total_lost_on_that_venue) = cursor.fetchone()

    conn.close()

    return {
        "total_match_played": total_match_played,
        "total_match_wins": total_match_wins,
        "total_toss_wins": total_toss_wins,
        "highest_score": highest_score,
        "lowest_score": lowest_score, 
        "highest_score_against": highest_score_against,
        "lowest_score_against": lowest_score_against,
        "most_win_against_team": most_win_against_team,
        "total_win_against_that_team": total_win_against_that_team,
        "most_lost_against_team": most_lost_against_team,
        "total_lost_against_that_team": total_lost_against_that_team,
        "most_win_on_venue": most_win_on_venue,
        "total_win_on_that_venue": total_win_on_that_venue,
        "most_lost_on_venue": most_lost_on_venue,
        "total_lost_on_that_venue": total_lost_on_that_venue,
        "total_runs": total_runs,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "total_wickets": total_wickets,
    }

print(get_player_stats("Mumbai Indians"))
