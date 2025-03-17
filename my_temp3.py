import sqlite3

DB_PATH = "ipl_stats.db"

def get_player_stats(team_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Career totals grouped by year
# Matches at Wankhede
    cursor.execute('''
    SELECT distinct venue
    from matches
''')
    total = cursor.fetchall()
    print(total)


    conn.close()

    # return {
    #     "batting_stats": batting_stats,
    #     "got_out_stats": got_out_stats,
    #     "bowling_stats": bowling_stats,
    #     "innings_as_batsman": innings_as_batsman,
    #     "innings_as_bowler": innings_as_bowler,
    #     "catches": catches,
    #     "ball_faced": total_ball_faced,
    #     "ball_thrown":total_ball_thrown,
    # }

print(get_player_stats("Mumbai Indians"))
