import sqlite3
import pandas as pd

# File paths
deliveries_path = "D:\Programming\Python\projects\cric_insight1\database\deliveries.csv"
matches_path = "D:\Programming\Python\projects\cric_insight1\database\matches.csv"

# Load CSV data
deliveries_df = pd.read_csv(deliveries_path)
matches_df = pd.read_csv(matches_path)

# Connect to SQLite database
conn = sqlite3.connect('ipl_stats.db')
cursor = conn.cursor()

# Create matches table
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    season TEXT,
    city TEXT,
    date TEXT,
    match_type TEXT,
    player_of_match TEXT,
    venue TEXT,
    team1 TEXT,
    team2 TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    result TEXT,
    result_margin REAL,
    target_runs REAL,
    target_overs REAL,
    super_over TEXT,
    method TEXT,
    umpire1 TEXT,
    umpire2 TEXT
);
''')

# Create deliveries table with composite primary key
cursor.execute('''
CREATE TABLE IF NOT EXISTS deliveries (
    match_id INTEGER,
    inning INTEGER,
    batting_team TEXT,
    bowling_team TEXT,
    over INTEGER,
    ball INTEGER,
    batter TEXT,
    bowler TEXT,
    non_striker TEXT,
    batsman_runs INTEGER,
    extra_runs INTEGER,
    total_runs INTEGER,
    extras_type TEXT,
    is_wicket INTEGER,
    player_dismissed TEXT,
    dismissal_kind TEXT,
    fielder TEXT,
    PRIMARY KEY (match_id, inning, over, ball),
    FOREIGN KEY (match_id) REFERENCES matches (id)
);
''')

# Insert data into tables
matches_df.to_sql('matches', conn, if_exists='replace', index=False)
deliveries_df.to_sql('deliveries', conn, if_exists='replace', index=False)

# Create indexes for faster queries
cursor.execute('CREATE INDEX IF NOT EXISTS idx_batter ON deliveries (batter);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bowler ON deliveries (bowler);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_batting_team ON deliveries (batting_team);')

# Commit and close
conn.commit()
conn.close()

print("Database and tables created successfully, and data imported.")

