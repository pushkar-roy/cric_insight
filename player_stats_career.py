import sqlite3

DB_PATH = "ipl_stats.db"

def get_player_stats(player_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT COUNT(DISTINCT player) 
    FROM (
        SELECT batter AS player FROM deliveries WHERE inning <= 2
        UNION 
        SELECT bowler AS player FROM deliveries WHERE inning <= 2
    );
    ''')
    (total_players,) = cursor.fetchone()
    print(total_players)


    # Fetch Total Runs Scored, Fours, Sixes and Their Ranks
    cursor.execute('''
    WITH BattingStats AS (
    SELECT batter, 
           SUM(batsman_runs) AS total_runs,
           SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END) AS total_fours,
           SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS total_sixes
    FROM deliveries
    WHERE inning <= 2
    GROUP BY batter
    ),
    RankedBattingStats AS (
    SELECT batter, 
           COALESCE(total_runs, 0) AS total_runs, 
           COALESCE(total_fours, 0) AS total_fours, 
           COALESCE(total_sixes, 0) AS total_sixes,
           COALESCE(RANK() OVER (ORDER BY total_runs DESC), NULL) AS total_runs_rank, 
           COALESCE(RANK() OVER (ORDER BY total_fours DESC), NULL) AS total_fours_rank, 
           COALESCE(RANK() OVER (ORDER BY total_sixes DESC), NULL) AS total_sixes_rank
    FROM BattingStats
    )
    SELECT total_runs, total_fours, total_sixes, total_runs_rank, total_fours_rank, total_sixes_rank
    FROM RankedBattingStats
    WHERE batter = ?;

    ''', (player_name,))
    (total_runs_scored, total_fours, total_sixes, total_runs_rank, total_fours_rank, total_sixes_rank) = cursor.fetchone() or (0, 0, 0, None, None, None)
 
 
    # Fetch Total Runs Given, Wickets Taken and Their Ranks
    cursor.execute('''
    WITH BowlerStats AS (
    SELECT bowler, 
           SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN extra_runs ELSE 0 END) AS total_runs_given,
           SUM(CASE WHEN dismissal_kind IN ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") THEN 1 ELSE 0 END) AS total_wickets_taken
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler
    ),
    RankedBowlerStats AS (
    SELECT bowler, 
           COALESCE(total_runs_given, 0) AS total_runs_given, 
           COALESCE(total_wickets_taken, 0) AS total_wickets_taken,
           COALESCE(RANK() OVER (ORDER BY total_runs_given ASC), NULL) AS total_runs_given_rank,  
           COALESCE(RANK() OVER (ORDER BY total_wickets_taken DESC), NULL) AS total_wickets_taken_rank
    FROM BowlerStats
    )
    SELECT total_runs_given, total_wickets_taken, total_runs_given_rank, total_wickets_taken_rank
    FROM RankedBowlerStats
    WHERE bowler = ?;

    ''', (player_name,))
    (total_runs_given, total_wickets_taken, total_runs_given_rank, total_wickets_rank) = cursor.fetchone() or (0, 0, None, None)


    # Fetch Total Catches and Rank
    cursor.execute('''
    WITH CatchStats AS (
    SELECT fielder AS player, COUNT(*) AS total_catches
    FROM deliveries
    WHERE dismissal_kind = 'caught'
    GROUP BY fielder
    UNION ALL
    SELECT bowler AS player, COUNT(*) AS total_catches
    FROM deliveries
    WHERE dismissal_kind = 'caught and bowled'
    GROUP BY bowler
    ),
    RankedCatchStats AS (
    SELECT player, 
           COALESCE(SUM(total_catches), 0) AS total_catches,
           COALESCE(RANK() OVER (ORDER BY SUM(total_catches) DESC), NULL) AS total_catches_rank
    FROM CatchStats
    GROUP BY player
    )
    SELECT total_catches, total_catches_rank
    FROM RankedCatchStats
    WHERE player = ?;

    ''', (player_name,))
    (total_catches, total_catches_rank) = cursor.fetchone() or (0, None)

    # Fetch Total Balls Faced and Rank
    cursor.execute('''
    WITH BowlerBalls AS (
    SELECT bowler, 
           COUNT(ball) - SUM(CASE WHEN extras_type IN ("wides", "noballs") THEN 1 ELSE 0 END) AS total_balls_thrown
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler
    ),
    RankedBowlerBalls AS (
    SELECT bowler, 
           COALESCE(total_balls_thrown, 0) AS total_balls_thrown,
           COALESCE(RANK() OVER (ORDER BY total_balls_thrown DESC), NULL) AS total_balls_thrown_rank
    FROM BowlerBalls
    )
    SELECT total_balls_thrown, total_balls_thrown_rank
    FROM RankedBowlerBalls
    WHERE bowler = ?;

    ''', (player_name,))
    (total_ball_thrown, total_ball_thrown_rank) = cursor.fetchone() or (0, None)

    
    cursor.execute('''
    WITH BatterStrikeRates AS (
    SELECT batter, 
           COALESCE(
               CASE 
                   WHEN COUNT(ball) - SUM(CASE WHEN extras_type = "wides" THEN 1 ELSE 0 END) > 0 
                   THEN SUM(batsman_runs) * 100.0 / 
                        (COUNT(ball) - SUM(CASE WHEN extras_type = "wides" THEN 1 ELSE 0 END)) 
                   ELSE 0 
               END, 0) AS batting_strike_rate
    FROM deliveries
    WHERE inning <= 2
    GROUP BY batter
    ),
    RankedBatterStrikeRates AS (
    SELECT batter, 
           batting_strike_rate,
           COALESCE(RANK() OVER (ORDER BY batting_strike_rate DESC), NULL) AS batting_strike_rate_rank
    FROM BatterStrikeRates
    )
    SELECT batting_strike_rate, batting_strike_rate_rank
    FROM RankedBatterStrikeRates
    WHERE batter = ?;

    ''', (player_name,))
    (batting_strike_rate, batting_strike_rate_rank) = cursor.fetchone() or (0, None)


    cursor.execute('''
WITH TotalRuns AS (
    SELECT 
        batter, 
        SUM(batsman_runs) AS total_runs
    FROM deliveries
    WHERE inning <= 2
    GROUP BY batter
),
TotalOuts AS (
    SELECT 
        player_dismissed AS batter, 
        COUNT(*) AS total_times_out
    FROM deliveries
    WHERE player_dismissed IS NOT NULL AND inning <= 2
    GROUP BY player_dismissed
),
BattingAverages AS (
    SELECT 
        r.batter,
        r.total_runs,
        COALESCE(o.total_times_out, 0) AS total_times_out,
        COALESCE(r.total_runs * 1.0 / NULLIF(o.total_times_out, 0), 0) AS batting_average,
        RANK() OVER (ORDER BY COALESCE(r.total_runs * 1.0 / NULLIF(o.total_times_out, 0), 0) DESC) AS ranking
    FROM TotalRuns r
    LEFT JOIN TotalOuts o ON r.batter = o.batter
)
SELECT ranking, batting_average 
FROM BattingAverages 
WHERE batter = ?;

    ''', (player_name,))
    (batting_average_rank, batting_average) = cursor.fetchone() or (None, 0)


    cursor.execute('''
    WITH BowlerAverages AS (
    SELECT 
        bowler, 
        SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN extra_runs ELSE 0 END) AS total_runs_given,
        SUM(CASE WHEN dismissal_kind IN ('caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket') THEN 1 ELSE 0 END) AS total_wickets
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler
    ),
    RankedBowlerAverages AS (
    SELECT 
        bowler, 
        COALESCE(
            CASE 
                WHEN total_wickets > 0 THEN total_runs_given * 1.0 / total_wickets 
                ELSE total_runs_given 
            END, 0) AS bowling_average,
        COALESCE(RANK() OVER (ORDER BY 
            CASE 
                WHEN total_wickets > 0 THEN total_runs_given * 1.0 / total_wickets 
                ELSE total_runs_given 
            END ASC), NULL) AS ranking
    FROM BowlerAverages
    )
    SELECT ranking, bowling_average
    FROM RankedBowlerAverages
    WHERE bowler = ?;

    ''', (player_name,))
    (bowling_rank, bowling_average) = cursor.fetchone() or (None, 0)


    cursor.execute('''
    WITH BowlerStrikeRates AS (
    SELECT 
        bowler, 
        COUNT(ball) - SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN 1 ELSE 0 END) AS total_balls_bowled,
        SUM(CASE WHEN dismissal_kind IN ('caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket') THEN 1 ELSE 0 END) AS total_wickets
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler
    ),
    RankedBowlerStrikeRates AS (
    SELECT 
        bowler, 
        COALESCE(
            CASE 
                WHEN total_wickets > 0 THEN total_balls_bowled * 1.0 / total_wickets 
                ELSE total_balls_bowled 
            END, 0) AS bowling_strike_rate,
        COALESCE(RANK() OVER (ORDER BY 
            CASE 
                WHEN total_wickets > 0 THEN total_balls_bowled * 1.0 / total_wickets 
                ELSE total_balls_bowled 
            END ASC), NULL) AS ranking
    FROM BowlerStrikeRates
    )
    SELECT ranking, bowling_strike_rate
    FROM RankedBowlerStrikeRates
    WHERE bowler = ?;
    
    ''', (player_name,))
    (bowling_strike_rate_rank, bowling_strike_rate) = cursor.fetchone() or (None, 0)


    cursor.execute('''
    WITH BowlerEconomy AS (
    SELECT 
        bowler, 
        COALESCE(
            (SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN extra_runs ELSE 0 END)) * 6.0 / 
            NULLIF(COUNT(ball) - SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN 1 ELSE 0 END), 0), 
        0) AS economy
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler
    ),
    RankedEconomy AS (
    SELECT 
        bowler, 
        economy,
        RANK() OVER (ORDER BY economy ASC) AS ranking
    FROM BowlerEconomy
    )
    SELECT ranking, economy
    FROM RankedEconomy
    WHERE bowler = ?;
    ''', (player_name,))

    (economy_rank, economy) = cursor.fetchone() or (None, 0)


    # Fetch Five-Wicket Hauls and Rank
    cursor.execute('''
    WITH MatchWiseWickets AS (
    SELECT 
        bowler, 
        match_id,
        SUM(CASE WHEN dismissal_kind IN ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") 
                 THEN 1 ELSE 0 END) AS total_wickets
    FROM deliveries 
    WHERE inning <= 2
    GROUP BY bowler, match_id
    ),  
    FiveWicketHauls AS (
    SELECT 
        bowler, 
        COUNT(*) AS five_wickets
    FROM MatchWiseWickets
    WHERE total_wickets >= 5
    GROUP BY bowler
    ),
    RankedFiveWickets AS (
    SELECT 
        bowler, 
        five_wickets,
        RANK() OVER (ORDER BY five_wickets DESC) AS ranking
    FROM FiveWicketHauls
    )
    SELECT COALESCE(five_wickets, 0), COALESCE(ranking, NULL)
    FROM RankedFiveWickets
    WHERE bowler = ?;
    ''', (player_name,))

    (five_wickets, five_wickets_rank) = cursor.fetchone() or (0, None)


    # Fetch Highest Score and Rank
    cursor.execute('''
    WITH MatchWiseScores AS (
    SELECT 
        batter, 
        match_id, 
        SUM(batsman_runs) AS match_runs
    FROM deliveries 
    WHERE inning <= 2
    GROUP BY batter, match_id
    ),
    RankedScores AS (
    SELECT 
        batter, 
        MAX(match_runs) AS high_score,  
        RANK() OVER (ORDER BY MAX(match_runs) DESC) AS ranking
    FROM MatchWiseScores
    GROUP BY batter
    )
    SELECT COALESCE(high_score, 0), COALESCE(ranking, NULL)
    FROM RankedScores
    WHERE batter = ?;
    ''', (player_name,))

    (high_score, high_score_rank) = cursor.fetchone() or (0, None)


    # Fetch Total Hundreds and Rank
    cursor.execute('''
    WITH MatchWiseScores AS (
    SELECT 
        batter, 
        match_id, 
        SUM(batsman_runs) AS total_runs
    FROM deliveries 
    WHERE inning <= 2
    GROUP BY batter, match_id
    ),
    HundredCount AS (
    SELECT 
        batter, 
        COUNT(CASE WHEN total_runs >= 100 THEN 1 END) AS total_hundreds
    FROM MatchWiseScores
    GROUP BY batter
    ),
    RankedHundreds AS (
    SELECT 
        batter, 
        total_hundreds, 
        RANK() OVER (ORDER BY total_hundreds DESC) AS ranking
    FROM HundredCount
    )
    SELECT COALESCE(total_hundreds, 0), COALESCE(ranking, NULL)
    FROM RankedHundreds
    WHERE batter = ?;
    ''', (player_name,))

    (hundreds, hundreds_rank) = cursor.fetchone() or (0, None)


    # Fetch Total Fifties and Rank
    cursor.execute('''
    WITH MatchWiseScores AS (
    SELECT 
        batter, 
        match_id, 
        SUM(batsman_runs) AS total_runs
    FROM deliveries 
    WHERE inning <= 2
    GROUP BY batter, match_id
    ),
    FiftyCount AS (
    SELECT 
        batter, 
        COUNT(CASE WHEN total_runs >= 50 AND total_runs < 100 THEN 1 END) AS total_fifties
    FROM MatchWiseScores
    GROUP BY batter
    ),
    RankedFifties AS (
    SELECT 
        batter, 
        total_fifties, 
        RANK() OVER (ORDER BY total_fifties DESC) AS ranking
    FROM FiftyCount
    )
    SELECT COALESCE(total_fifties, 0), COALESCE(ranking, NULL)
    FROM RankedFifties
    WHERE batter = ?;
    ''', (player_name,))

    (fifties, fifties_rank) = cursor.fetchone() or (0, None)


    cursor.execute('''
        WITH BowlingFigures AS (
            -- Compute wickets and runs for each bowler per match
            SELECT 
                bowler, 
                match_id,
                SUM(CASE WHEN dismissal_kind IN ("caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket") 
                         THEN 1 ELSE 0 END) AS total_wicket,
                SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ("wides", "noballs") THEN extra_runs ELSE 0 END) AS total_runs
            FROM deliveries
            WHERE inning <= 2
            GROUP BY bowler, match_id
        ),
        RankedBowlingFigures AS (
            -- Rank bowling figures within each bowler
            SELECT
                bowler,
                match_id,
                total_wicket,
                total_runs,
                RANK() OVER (PARTITION BY bowler ORDER BY total_wicket DESC, total_runs ASC) AS figure_rank
            FROM BowlingFigures
        ),
        BestFigures AS (
            -- Get the best bowling figure per bowler
            SELECT
                bowler,
                total_wicket AS best_wickets,
                total_runs AS best_runs
            FROM RankedBowlingFigures
            WHERE figure_rank = 1
        ),
        RankedBowlers AS (
            -- Rank bowlers based on their best figures
            SELECT
                bowler,
                best_wickets || '/' || best_runs AS best_figure,
                RANK() OVER (ORDER BY best_wickets DESC, best_runs ASC) AS ranking
            FROM BestFigures
        )
        SELECT ranking, COALESCE(best_figure, '0/0')
        FROM RankedBowlers
        WHERE bowler = ?;
    ''', (player_name,))

    (best_figure_rank, best_figure) = cursor.fetchone() or (None, "0/0")


    
    cursor.execute('''
    WITH OverWiseData AS (
    SELECT 
        bowler,
        match_id,
        over,
        SUM(batsman_runs) AS batsman_runs,
        SUM(CASE WHEN extras_type IN ('wides', 'noballs', 'penalty') THEN 1 ELSE 0 END) AS extra_runs
    FROM deliveries
    WHERE inning <= 2
    GROUP BY bowler, match_id, over
    ),
    MaidenOverCounts AS (
    SELECT 
        bowler, 
        COUNT(*) AS maiden_overs
    FROM OverWiseData
    WHERE batsman_runs = 0 AND extra_runs = 0  -- Only count overs where no runs from bat and no wides/no-balls/penalties
    GROUP BY bowler
    ),
    RankedMaidenOvers AS (
    SELECT 
        bowler,
        maiden_overs,
        RANK() OVER (ORDER BY maiden_overs DESC) AS ranking
    FROM MaidenOverCounts
    )
    SELECT COALESCE(ranking, NULL), COALESCE(maiden_overs, 0)
    FROM RankedMaidenOvers
    WHERE bowler = ?;
    ''', (player_name,))

    (maiden_over_rank, maiden_overs) = cursor.fetchone() or (None, 0)


    conn.close()

    return {
        "total_runs_scored": (total_runs_scored, total_runs_rank),
        "total_runs_given": (total_runs_given, total_runs_given_rank),
        "total_fours_scored": (total_fours, total_fours_rank),
        "total_sixes_scored": (total_sixes, total_sixes_rank),
        "total_sixes_scored": (total_sixes, total_sixes_rank),
        "total_catches": (total_catches, total_catches_rank), 
        "total_ball_thrown": (total_ball_thrown, total_ball_thrown_rank),
        "total_wickets_taken": (total_wickets_taken, total_wickets_rank),
        "total_runs_given": (total_runs_given, total_runs_given_rank),
        "batting_strike_rate": (batting_strike_rate, batting_strike_rate_rank),
        "batting_avg": (batting_average, batting_average_rank),
        "bowling_avg": (bowling_average, bowling_rank),
        "bowling_strike_rate": (bowling_strike_rate, bowling_strike_rate_rank),
        "economy": (economy, economy_rank),
        "maiden_overs": (maiden_overs, maiden_over_rank),
        "five_wickets": (five_wickets, five_wickets_rank),
        "hundreds": (hundreds, hundreds_rank),
        "fifties": (fifties, fifties_rank),
        "high_score": (high_score, high_score_rank),
        "best_figure": (best_figure, best_figure_rank),
    }

print(get_player_stats("SK Raina"))
