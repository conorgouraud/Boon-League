from flask import Flask, render_template, request, redirect, url_for, flash
import pycountry
from leaderboard import *
from games import *
import psycopg2
import os

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
        ranking = []
        raw_inputs = []

        # capture ALL inputs (including blanks)
        for i in range(1, 8):
            name = request.form.get(f"player{i}", "").strip()
            raw_inputs.append(name)

        # detect gaps BEFORE filtering
        for i in range(len(raw_inputs)):
            if raw_inputs[i] and any(raw_inputs[j] == "" for j in range(i)):
                flash(f"Error: Cannot fill Player {i+1} before filling previous positions.", "error")
                return redirect(url_for("record_game_view"))

        # remove blanks after validation
        ranking = [name for name in raw_inputs if name]

        comment = request.form.get("comment", "").strip() or None

        if len(ranking) < 3:
            flash("Error: At least 3 players required.", "error")
            return redirect(url_for("record_game_view"))

        try:
            record_game(ranking, comment)
            flash("Game recorded successfully!", "success")
        except Exception as e:
            flash(f"Error recording game: {str(e)}", "error")

        return redirect(url_for("show_leaderboard"))

    return render_template("record_game.html")

# ------------------- GAMES HISTORY -------------------
@app.route("/games-history")
def games_history():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT pos1, pos2, pos3, pos4, pos5, pos6, pos7, comment, played_at
        FROM games
        ORDER BY played_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    games = []
    for r in rows:
        games.append({
            "positions": [p for p in r[:7] if p],
            "comment": r[7],
            "played_at": r[8].strftime("%Y-%m-%d %H:%M:%S")
        })

    return render_template("games_history.html", games=games)

# ------------------- RUN -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=0)