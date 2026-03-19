from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import pycountry
from datetime import datetime

from rating import *
from create_delete_players import *

app = Flask(__name__)
app.secret_key = "1234"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "boonleague.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

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
        country = request.form.get("country", "").strip()

        if not name:
            flash("Name cannot be empty", "error")
            return redirect(url_for("create_player"))

        if not country:
            flash("Please select a country", "error")
            return redirect(url_for("create_player"))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT name FROM players WHERE LOWER(name) = LOWER(?)", (name,))
        exists = cur.fetchone()

        if exists:
            flash(f"Player '{name}' already exists!", "error")
            conn.close()
            return redirect(url_for("create_player"))

        cur.execute("""
            INSERT INTO players (name, country, added_at)
            VALUES (?, ?, ?)
        """, (name, country, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        flash(f"Player '{name}' added successfully!", "success")
        return redirect(url_for("existing_players"))

    countries = [c.name for c in pycountry.countries]
    return render_template("create_player.html", countries=countries)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=0)
