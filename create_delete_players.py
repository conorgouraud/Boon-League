import sqlite3
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(SCRIPT_DIR, "boonleague.db")

def get_connection():
    return sqlite3.connect(db_path)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            country TEXT,
            added_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_players():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, country, added_at FROM players")
    rows = cur.fetchall()
    conn.close()

    return [
        {"name": r[0], "country": r[1], "added_at": r[2]}
        for r in rows
    ]

def add_player(name, country=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO players (name, country, added_at) VALUES (?, ?, ?)",
            (name, country, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        print(f"Added {name}.")
    except sqlite3.IntegrityError:
        print(f"{name} already exists.")
    finally:
        conn.close()

def delete_player(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM players WHERE name = ?", (name,))
    conn.commit()

    if cur.rowcount == 0:
        print(f"{name} does not exist.")
    else:
        print(f"Deleted {name}.")

    conn.close()

def delete_all_players():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM players")
    conn.commit()
    conn.close()
    print("All players deleted.")
