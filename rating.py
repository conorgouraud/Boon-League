import csv
import trueskill
import os

from datetime import datetime
from create_delete_players import *

env = trueskill.TrueSkill(draw_probability=0.0)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYERS_FILE = os.path.join(SCRIPT_DIR, "players.csv")
RATINGS_FILE = os.path.join(SCRIPT_DIR, "ratings.csv")

def load_ratings():
    ratings = {}
    try:
        with open(RATINGS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ratings[row["name"]] = trueskill.Rating(
                    mu=float(row["mu"]),
                    sigma=float(row["sigma"])
                )
    except FileNotFoundError:
        pass
    return ratings


def save_ratings(ratings):
    with open(RATINGS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "mu", "sigma"])
        for name, rating in ratings.items():
            writer.writerow([name, rating.mu, rating.sigma])


# ------------------- Record Game -------------------

def record_game(ranking):
    """
    ranking: list of player names in finishing order
    Example:
        ["Alice", "Bob", "Charlie"]  # Alice won
    """

    # Step 1: Load existing players
    existing_players = load_players()
    existing_names = [p["name"] for p in existing_players]

    # Step 2: Check if all players exist in players.csv
    missing_players = [name for name in ranking if name not in existing_names]
    if missing_players:
        print("These players do not exist in players.csv:", ", ".join(missing_players))
        return

    # Step 3: Load current ratings
    ratings = load_ratings()

    # Step 4: Add default rating for any player missing in ratings.csv
    for name in ranking:
        # Use the exact name as it appears in players.csv
        players_csv_name = next(p["name"] for p in existing_players if p["name"] == name)
        if players_csv_name not in ratings:
            ratings[players_csv_name] = env.create_rating()

    # Step 5: Prepare teams and ranks
    teams = [[ratings[next(p["name"] for p in existing_players if p["name"] == name)]] for name in ranking]
    ranks = list(range(len(ranking)))
    new_ratings = env.rate(teams, ranks=ranks)

    # Step 6: Update ratings
    for i, name in enumerate(ranking):
        players_csv_name = next(p["name"] for p in existing_players if p["name"] == name)
        ratings[players_csv_name] = new_ratings[i][0]

    # Step 7: Save back to CSV
    save_ratings(ratings)

    # Step 8: Print updated ratings
    print("Updated ratings:")
    for name in ranking:
        players_csv_name = next(p["name"] for p in existing_players if p["name"] == name)
        r = ratings[players_csv_name]
        print(f"{players_csv_name}: mu={r.mu:.2f}, sigma={r.sigma:.2f}")

# ------------------- Rating Management -------------------

def reset_ratings():
    ratings = load_ratings()
    for name in ratings:
        ratings[name] = env.create_rating()
    save_ratings(ratings)
    print("All ratings reset to default.")


def add_rating(name):
    ratings = load_ratings()
    if name in ratings:
        print(f"{name} already exists.")
        return
    ratings[name] = env.create_rating()
    save_ratings(ratings)
    print(f"Added {name} with default rating.")


def delete_rating(name):
    ratings = load_ratings()
    if name not in ratings:
        print(f"{name} does not exist.")
        return
    del ratings[name]
    save_ratings(ratings)
    print(f"Deleted {name}.")


def delete_all_ratings():
    with open(RATINGS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "mu", "sigma"])
    print("All ratings deleted.")