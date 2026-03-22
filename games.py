import psycopg2
from datetime import datetime
import trueskill
from leaderboard import get_connection, env, update_player_rating, load_leaderboard

env = trueskill.TrueSkill(draw_probability=0.0)

def init_games_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            pos1 TEXT NOT NULL,
            pos2 TEXT NOT NULL,
            pos3 TEXT NOT NULL,
            pos4 TEXT,
            pos5 TEXT,
            pos6 TEXT,
            pos7 TEXT,
            comment TEXT,
            played_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    conn.commit()
    conn.close()

# ------------------- RECORD GAME -------------------

def record_game(ranking, comment=None):
    """
    ranking: list of player names in finishing order (min 3, max 7)
    """

    init_games_table()

    # ------------------- VALIDATION -------------------

    # 1. Minimum / Maximum players
    if len(ranking) < 3:
        raise ValueError("At least 3 players must be added.")

    if len(ranking) > 7:
        raise ValueError("Maximum 7 players allowed.")

    # 2. No duplicates
    if len(ranking) != len(set(ranking)):
        duplicates = [name for name in set(ranking) if ranking.count(name) > 1]
        raise ValueError(f"Duplicate players not allowed: {', '.join(duplicates)}")

    # 3. No gaps (e.g. player5 but no player4)
    positions = ranking + [None] * (7 - len(ranking))
    for i in range(1, 7):
        if positions[i] and not positions[i-1]:
            raise ValueError(f"Cannot have Player {i+1} without Player {i}")

    # 4. Check all players EXIST in leaderboard
    existing_players = [p["name"] for p in load_leaderboard()]
    missing_players = [name for name in ranking if name not in existing_players]

    if missing_players:
        raise ValueError(
            "These players do not exist and must be created first: "
            + ", ".join(missing_players)
        )

    # ------------------- LOAD RATINGS -------------------

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, mu, sigma FROM leaderboard")
    rows = cur.fetchall()

    ratings = {
        r[0]: trueskill.Rating(mu=float(r[1]), sigma=float(r[2]))
        for r in rows
    }

    # ------------------- TRUE SKILL -------------------

    teams = [[ratings[name]] for name in ranking]
    ranks = list(range(len(ranking)))

    new_ratings = env.rate(teams, ranks=ranks)

    # ------------------- SAVE GAME FIRST -------------------

    cur.execute("""
        INSERT INTO games (pos1, pos2, pos3, pos4, pos5, pos6, pos7, comment, played_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (*positions, comment))

    # ------------------- UPDATE RATINGS -------------------

    for i, name in enumerate(ranking):
        r = new_ratings[i][0]
        update_player_rating(name, r, increment_games=1)

    conn.commit()
    conn.close()

    # ------------------- SUCCESS LOG -------------------

    print("Game recorded successfully. Ratings updated:")
    for i, name in enumerate(ranking):
        r = new_ratings[i][0]
        print(f"{name}: mu={r.mu:.2f}, sigma={r.sigma:.2f}, score={r.mu - 3*r.sigma:.2f}")