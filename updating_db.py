import sqlite3

DB_PATH = "ipl_stats.db"

# Mapping of old team names to new team names
TEAM_NAME_MAPPING = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiant": "Rising Pune Supergiants",
    "Royal Challengers Bangaloru": "Royal Challengers Bengaluru",
}

def update_team_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List of tables and columns where team names need to be updated
    tables_and_columns = [
        ("matches", ["team1", "team2", "winner", "toss_winner"]),
        ("deliveries", ["batting_team", "bowling_team"])
    ]

    for old_name, new_name in TEAM_NAME_MAPPING.items():
        for table, columns in tables_and_columns:
            for column in columns:
                query = f'''
                    UPDATE {table}
                    SET {column} = ?
                    WHERE {column} = ?
                '''
                cursor.execute(query, (new_name, old_name))
                print(f"Updated {old_name} to {new_name} in {table}.{column}")

    conn.commit()
    conn.close()
    print("Team names updated successfully!")

update_team_names()
