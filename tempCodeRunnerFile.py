    cursor.execute('''
    SELECT ranking, economy
    FROM (
        SELECT 
            bowler, 
            (SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN extra_runs ELSE 0 END)) / 
                     (COUNT(ball) - SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN 1 ELSE 0 END)) * 6 AS economy,
            RANK() OVER (ORDER BY (SUM(batsman_runs) + SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN extra_runs ELSE 0 END)) /
                                    (COUNT(ball) - SUM(CASE WHEN extras_type IN ('wides', 'noballs') THEN 1 ELSE 0 END)) * 6 ASC) AS ranking
        FROM deliveries
        WHERE inning <= 2
        GROUP BY bowler
    )
    WHERE bowler = ?;
    ''', (player_name,))
    (economy_rank, economy) = cursor.fetchone() or (None, 0)