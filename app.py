from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pycountry
from datetime import datetime

# Import your rewritten Postgres modules
from ratings_db import load_ratings
from players_db import load_players, add_player

app = Flask(__name__)
app.secret_key = "1234"

# ------------------- ROUTES -------------------

@app.route("/")
def leaderboard():
    players = load_ratings()

    # Convert dict → sorted list for template
    sorted_players = sorted(
        players.values(),
        key=lambda p: p["score"],
        reverse=True
    )

    return render_template("leaderboard.html", players=sorted_players)


@app.route("/players")
def existing_players():
    players = load_players()
    return render_template("players.html", players=players)


@app.route("/create-player", methods=["GET", "POST"])
def create_player():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()

        if not name:
            flash("Name cannot be empty", "error")
            return redirect(url_for("create_player"))

        if not country:
            flash("Please select a country", "error")
            return redirect(url_for("create_player"))

        # Use your Postgres add_player() function
        try:
            add_player(name, country)
            flash(f"Player '{name}' added successfully!", "success")
        except Exception as e:
            flash(f"Error adding player: {str(e)}", "error")

        return redirect(url_for("existing_players"))

    # Full country list
    countries = [c.name for c in pycountry.countries]
    return render_template("create_player.html", countries=countries)


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=0)
