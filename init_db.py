import sqlite3

# Connect to database 
conn = sqlite3.connect("sightings.db")
c = conn.cursor()

# Create table
c.execute("""
CREATE TABLE IF NOT EXISTS sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    notes TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Database initialized.")
