from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

app = Flask(__name__)
app.secret_key = "1234"
RATINGS_FILE = os.path.join(os.path.dirname(__file__), "ratings.csv")
PLAYERS_FILE = os.path.join(os.path.dirname(__file__), "players.csv")


def load_ratings():
    players = []
    try:
        with open(RATINGS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                players.append({
                    "name": row["name"],
                    "mu": float(row["mu"]),
                    "sigma": float(row["sigma"]),
                    "score": float(row["mu"]) - 3*float(row["sigma"])
                })
        players.sort(key=lambda x: x["score"], reverse=True)
    except FileNotFoundError:
        pass
    return players


def load_players():
    players = []
    try:
        with open(PLAYERS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                players.append({
                    "name": row["name"],
                    "added_at": row["added_at"]
                })
    except FileNotFoundError:
        pass
    return players


@app.route("/")
def leaderboard():
    players = load_ratings()
    return render_template("leaderboard.html", players=players)


@app.route("/players")
def existing_players():
    players = load_players()
    return render_template("players.html", players=players)


@app.route("/create-player", methods=["GET", "POST"])
def create_player():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name cannot be empty", "error")
            return redirect(url_for("create_player"))

        existing_players = load_players()
        existing_lower = [p["name"].lower() for p in existing_players]
        if name.lower() in existing_lower:
            flash(f"Player '{name}' already exists!", "error")
            return redirect(url_for("create_player"))

        from datetime import datetime
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        PLAYERS_FILE = os.path.join(SCRIPT_DIR, "players.csv")
        import csv
        with open(PLAYERS_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "added_at"])
            if f.tell() == 0:  # Write header if file empty
                writer.writeheader()
            writer.writerow({
                "name": name,
                "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        flash(f"Player '{name}' added successfully!", "success")
        return redirect(url_for("existing_players"))

    return render_template("create_player.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=0)