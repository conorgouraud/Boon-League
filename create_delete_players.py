import csv
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
players_csv = os.path.join(SCRIPT_DIR, "players.csv")

def load_players():
    players = []
    try:
        with open(players_csv, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                players.append(row)
    except FileNotFoundError:
        pass
    return players

def save_players(players):
    with open(players_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "added_at"])
        writer.writeheader()
        for player in players:
            writer.writerow(player)

def add_player(name):
    players = load_players()

    if any(p["name"] == name for p in players):
        print(f"{name} already exists.")
        return

    new_player = {
        "name": name,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(players_csv, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "added_at"])
        if f.tell() == 0:  
            writer.writeheader()
        writer.writerow(new_player)

    print(f"Added {name}.")

def delete_player(name):
    players = load_players()
    new_players = [p for p in players if p["name"] != name]

    if len(new_players) == len(players):
        print(f"{name} does not exist.")
        return

    save_players(new_players)
    print(f"Deleted {name}.")

def delete_all_players():
    with open(players_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "added_at"])
        writer.writeheader()
    print("All players deleted.")