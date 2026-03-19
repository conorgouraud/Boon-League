import psycopg2
import os
import trueskill
from datetime import datetime

env = trueskill.TrueSkill(draw_probability=0.0)

# Render provides DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_ratings_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            mu FLOAT NOT NULL,
            sigma FLOAT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def load_players():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM players ORDER BY name ASC")
    rows = cur.fetchall()

    conn.close()

    return [{"name": r[0]} for r in rows]

# ------------------- Rating Loading -------------------

def load_ratings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, mu, sigma FROM ratings")
    rows = cur.fetchall()
    conn.close()

    ratings = {}

    for name, mu, sigma in rows:
        mu = float(mu)
        sigma = float(sigma)
        score = mu - 3 * sigma

        ratings[name] = {
            "name": name,
            "mu": mu,
            "sigma": sigma,
            "score": score
        }

    return ratings

# ------------------- Save Rating -------------------

def save_rating_to_db(name, rating):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ratings (name, mu, sigma)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            mu = EXCLUDED.mu,
            sigma = EXCLUDED.sigma
    """, (name, rating.mu, rating.sigma))

    conn.commit()
    conn.close()

# ------------------- Record Game -------------------

def record_game(ranking):
    """
    ranking: list of player names in finishing order
    Example: ["Alice", "Bob", "Charlie"]
    """

    # Load existing players
    existing_players = load_players()
    existing_names = [p["name"] for p in existing_players]

    # Check for missing players
    missing = [name for name in ranking if name not in existing_names]
    if missing:
        print("These players do not exist:", ", ".join(missing))
        return

    # Load ratings
    ratings = load_ratings()

    # Ensure all players have a rating
    for name in ranking:
        if name not in ratings:
            r = env.create_rating()
            ratings[name] = {
                "name": name,
                "mu": r.mu,
                "sigma": r.sigma,
                "score": r.mu - 3 * r.sigma
            }

    # Prepare TrueSkill inputs
    teams = [[env.Rating(mu=ratings[name]["mu"], sigma=ratings[name]["sigma"])] for name in ranking]
    ranks = list(range(len(ranking)))

    # Compute new ratings
    new_ratings = env.rate(teams, ranks=ranks)

    # Save updated ratings
    for i, name in enumerate(ranking):
        updated = new_ratings[i][0]
        save_rating_to_db(name, updated)

    print("Updated ratings:")
    for name in ranking:
        r = ratings[name]
        print(f"{name}: mu={r['mu']:.2f}, sigma={r['sigma']:.2f}")

# ------------------- Rating Management -------------------

def reset_ratings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE ratings SET mu = %s, sigma = %s", (env.mu, env.sigma))
    conn.commit()
    conn.close()

    print("All ratings reset to default.")

def add_rating(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM ratings WHERE name = %s", (name,))
    if cur.fetchone():
        print(f"{name} already exists.")
        conn.close()
        return

    rating = env.create_rating()

    cur.execute(
        "INSERT INTO ratings (name, mu, sigma) VALUES (%s, %s, %s)",
        (name, rating.mu, rating.sigma)
    )

    conn.commit()
    conn.close()

    print(f"Added {name} with default rating.")

def delete_rating(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM ratings WHERE name = %s", (name,))
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
