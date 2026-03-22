import psycopg2
import os
from datetime import datetime
import trueskill

env = trueskill.TrueSkill(draw_probability=0.0)

DATABASE_URL = os.environ.get("DATABASE_URL") or \
    "postgresql://boonleague_db_user:9gJagU3PNzvf9iCD7BBXworXyaQc339Z@dpg-d6u1au7kijhs73feje20-a.frankfurt-postgres.render.com/boonleague_db"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# ------------------- Leaderboard -------------------

def init_leaderboard_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            country TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            rank INT DEFAULT NULL,
            mu FLOAT NOT NULL,
            sigma FLOAT NOT NULL,
            conservative_score FLOAT NOT NULL,
            last_updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            games_played INT NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Leaderboard table initialized.")

def load_leaderboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, country, created_at, mu, sigma, conservative_score, last_updated_at, games_played
        FROM leaderboard
    """)
    rows = cur.fetchall()
    conn.close()

    players = []
    for r in rows:
        players.append({
            "name": r[0],
            "country": r[1],
            "created_at": r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else None,
            "mu": float(r[3]),
            "sigma": float(r[4]),
            "conservative_score": float(r[5]),
            "last_updated_at": r[6].strftime("%Y-%m-%d %H:%M:%S") if r[6] else None,
            "games_played": r[7]
        })
    return players

def add_player(name, country=None):
    rating = env.create_rating()
    conservative_score = rating.mu - 3 * rating.sigma
    now = datetime.now()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leaderboard (name, country, mu, sigma, conservative_score, last_updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING
    """, (name, country, rating.mu, rating.sigma, conservative_score, now))
    conn.commit()
    conn.close()
    print(f"Added player: {name}")

def update_player_rating(name, rating, increment_games=0):
    now = datetime.now()
    conservative_score = rating.mu - 3 * rating.sigma

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE leaderboard
        SET mu=%s,
            sigma=%s,
            conservative_score=%s,
            last_updated_at=%s,
            games_played = games_played + %s
        WHERE name=%s
    """, (rating.mu, rating.sigma, conservative_score, now, increment_games, name))
    conn.commit()
    conn.close()