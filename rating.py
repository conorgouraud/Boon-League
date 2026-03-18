import csv
import trueskill

env = trueskill.TrueSkill(draw_probability=0.0)
CSV_FILE = "ratings.csv"


def load_ratings():
    players = {}
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            players[row["name"]] = trueskill.Rating(
                mu=float(row["mu"]),
                sigma=float(row["sigma"])
            )
    return players


def save_ratings(players):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "mu", "sigma"])
        for name, rating in players.items():
            writer.writerow([name, rating.mu, rating.sigma])


def record_game(ranking):
    """example: record_game(["Alice", "Bob", "Charlie"]) where Alice > Bob > Charlie"""
    players = load_ratings()

    missing = [name for name in ranking if name not in players]
    if missing:
        print("These players do not exist:", ", ".join(missing))
        return

    teams = [[players[name]] for name in ranking]
    ranks = list(range(len(ranking)))
    new_ratings = env.rate(teams, ranks=ranks)

    for i, name in enumerate(ranking):
        players[name] = new_ratings[i][0]

    save_ratings(players)

    print("Updated ratings:")
    for name in ranking:
        r = players[name]
        print(f"{name}: mu={r.mu:.2f}, sigma={r.sigma:.2f}")


def reset_ratings():
    players = load_ratings()

    for name in players:
        players[name] = env.create_rating()

    save_ratings(players)
    print("All ratings reset to default.")




################################################################################



def add_player(name):
    players = load_ratings()

    if name in players:
        print(f"{name} already exists.")
        return

    players[name] = env.create_rating()
    save_ratings(players)

    print(f"Added {name} with default rating.")


def delete_player(name):
    players = load_ratings()

    if name not in players:
        print(f"{name} does not exist.")
        return

    del players[name]
    save_ratings(players)

    print(f"Deleted {name}.")


def delete_all_players():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "mu", "sigma"]) 

    print("All players deleted.")


