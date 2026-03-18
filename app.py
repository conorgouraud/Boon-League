from flask import Flask, render_template
import csv

app = Flask(__name__)
CSV_FILE = "ratings.csv"

def load_ratings():
    players = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            players.append({
                "name": row["name"],
                "mu": float(row["mu"]),
                "sigma": float(row["sigma"]),
                "score": float(row["mu"]) - 3*float(row["sigma"])
            })
    # sort by conservative score
    players.sort(key=lambda x: x["score"], reverse=True)
    return players

@app.route("/")
def leaderboard():
    players = load_ratings()
    return render_template("leaderboard.html", players=players)

if __name__ == "__main__":
    app.run(debug=True)