import psycopg2
import os
from datetime import datetime

# Render provides DATABASE_URL in the environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_players_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            country TEXT,
            added_at TIMESTAMP NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def load_players():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, country, added_at FROM players ORDER BY name ASC")
    rows = cur.fetchall()

    conn.close()

    return [
        {"name": r[0], "country": r[1], "added_at": r[2].strftime("%Y-%m-%d %H:%M:%S")}
        for r in rows
    ]

def add_player(name, country=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO players (name, country, added_at) VALUES (%s, %s, %s)",
            (name, country, datetime.now())
        )
        conn.commit()
        print(f"Added {name}.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"{name} already exists.")
    finally:
        conn.close()

def delete_player(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM players WHERE name = %s", (name,))
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
