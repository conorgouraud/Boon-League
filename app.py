from flask import Flask, render_template, request, redirect, url_for, flash
import pycountry
from leaderboard import load_leaderboard, add_player
from games import record_game

app = Flask(__name__)
app.secret_key = "1234"

# ------------------- LEADERBOARD -------------------
@app.route("/")
def show_leaderboard():
    players = load_leaderboard()
    sorted_players = sorted(players, key=lambda p: p["conservative_score"], reverse=True)
    return render_template("leaderboard.html", players=sorted_players)

# ------------------- PLAYERS -------------------
@app.route("/players")
def show_players():
    players = load_leaderboard()
    sorted_players = sorted(players, key=lambda p: p["name"])
    return render_template("players.html", players=sorted_players)

# ------------------- CREATE PLAYER -------------------
@app.route("/create-player", methods=["GET", "POST"])
def create_player_view():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()

        if not name:
            flash("Name cannot be empty", "error")
            return redirect(url_for("create_player_view"))

        if not country:
            flash("Please select a country", "error")
            return redirect(url_for("create_player_view"))

        try:
            add_player(name, country)
            flash(f"Player '{name}' added successfully!", "success")
        except Exception as e:
            flash(f"Error adding player: {str(e)}", "error")

        return redirect(url_for("show_players"))

    countries = [c.name for c in pycountry.countries]
    return render_template("create_player.html", countries=countries)

# ------------------- RECORD GAME -------------------
@app.route("/record-game", methods=["GET", "POST"])
def record_game_view():
    if request.method == "POST":

        raw_players = []
        for i in range(1, 8):
            name = request.form.get(f"player{i}", "").strip()
            raw_players.append(name if name else None)

        # Remove trailing empty
        while raw_players and raw_players[-1] is None:
            raw_players.pop()

        comment = request.form.get("comment", "").strip() or None

        try:
            # Gap validation BEFORE filtering
            for i in range(1, len(raw_players)):
                if raw_players[i] and not raw_players[i-1]:
                    raise ValueError(f"Cannot fill position {i+1} if position {i} is empty.")

            ranking = [p for p in raw_players if p]

            missing_players = record_game(ranking, comment)

            if missing_players:
                flash(f"New players created: {', '.join(missing_players)}", "success")

            flash("Game recorded successfully!", "success")

        except ValueError as e:
            flash(str(e), "error")

        except Exception as e:
            flash(f"Unexpected error: {str(e)}", "error")

        return redirect(url_for("record_game_view"))

    return render_template("record_game.html")

# ------------------- RUN -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=0)