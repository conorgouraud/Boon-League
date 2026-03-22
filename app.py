from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pycountry
from datetime import datetime


from rating import *
from create_delete_players import *

app = Flask(__name__)
app.secret_key = "1234"

@app.route("/")
def leaderboard():
    players = load_ratings()

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

        try:
            add_player(name, country)
            flash(f"Player '{name}' added successfully!", "success")
        except Exception as e:
            flash(f"Error adding player: {str(e)}", "error")

        return redirect(url_for("existing_players"))

    countries = [c.name for c in pycountry.countries]
    return render_template("create_player.html", countries=countries)


if __name__ == "__main__":
    init_players_db()
    init_ratings_table()
    app.run(debug=True, host="0.0.0.0", port=0)
