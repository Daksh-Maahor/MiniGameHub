import csv
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
HISTORY_PATH = ROOT_DIR / "data" / "history.csv"

wins = Counter()
games = Counter()

with HISTORY_PATH.open() as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 4:
            winner, loser, date, game = row
            if winner != "Draw":
                wins[winner] += 1
            games[game] += 1

# Create a single figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Top 5 players by total wins
top5 = wins.most_common(5)
if top5:
    names = [n for n, c in top5]
    win_counts = [c for n, c in top5]
    ax1.bar(names, win_counts, color='skyblue')
    ax1.set_title("Top 5 Players by Total Wins")
    ax1.set_xlabel("Players")
    ax1.set_ylabel("Wins")
    ax1.tick_params(axis='x', rotation=45)

# Pie chart of most played games
if games:
    labels = list(games.keys())
    sizes = list(games.values())
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax2.set_title("Most Played Games by Frequency")
    ax2.axis('equal')

plt.tight_layout()
plt.show()