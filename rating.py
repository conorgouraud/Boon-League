import sqlite3
import trueskill
import os
from datetime import datetime

env = trueskill.TrueSkill(draw_probability=0.0)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "boonleague.db")

def get_connection():
    return sqlite3.connect(DB_PATH)


def load_players():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM players")
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0]} for r in rows]


def load_ratings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, mu, sigma FROM ratings")
    rows = cur.fetchall()
    conn.close()

    players = []
    for name, mu, sigma in rows:
        mu = float(mu)
        sigma = float(sigma)
        score = mu - 3 * sigma

        players.append({
            "name": name,
            "mu": mu,
            "sigma": sigma,
            "score": score
        })

    players.sort(key=lambda x: x["score"], reverse=True)
    return players


def save_rating_to_db(name, rating):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ratings (name, mu, sigma)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            mu = excluded.mu,
            sigma = excluded.sigma
    """, (name, rating.mu, rating.sigma))
    conn.commit()
    conn.close()


def record_game(ranking):
    """
    ranking: list of player names in finishing order
    Example: ["Alice", "Bob", "Charlie"]
    """
    existing_players = load_players()
    existing_names = [p["name"] for p in existing_players]

    missing = [name for name in ranking if name not in existing_names]
    if missing:
        print("These players do not exist:", ", ".join(missing))
        return

    ratings = load_ratings()
    for name in ranking:
        if name not in ratings:
            ratings[name] = env.create_rating()

    teams = [[ratings[name]] for name in ranking]
    ranks = list(range(len(ranking)))

    new_ratings = env.rate(teams, ranks=ranks)

    for i, name in enumerate(ranking):
        updated_rating = new_ratings[i][0]
        ratings[name] = updated_rating
        save_rating_to_db(name, updated_rating)

    print("Updated ratings:")
    for name in ranking:
        r = ratings[name]
        print(f"{name}: mu={r.mu:.2f}, sigma={r.sigma:.2f}")

# ------------------- Rating Management -------------------

def reset_ratings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ratings SET mu = ?, sigma = ?", 
                (env.mu, env.sigma))
    conn.commit()
    conn.close()
    print("All ratings reset to default.")


def add_rating(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM ratings WHERE name = ?", (name,))
    if cur.fetchone():
        print(f"{name} already exists.")
        conn.close()
        return

    rating = env.create_rating()
    cur.execute("INSERT INTO ratings (name, mu, sigma) VALUES (?, ?, ?)",
                (name, rating.mu, rating.sigma))
    conn.commit()
    conn.close()
    print(f"Added {name} with default rating.")


def delete_rating(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ratings WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    print(f"Deleted rating for {name}.")


def delete_all_ratings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ratings")
    conn.commit()
    conn.close()
    print("All ratings deleted.")
