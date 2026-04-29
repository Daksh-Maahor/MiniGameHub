"""Generate a dashboard of player and game statistics from history.csv."""

import csv
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

# Set a modern style for all charts.
plt.style.use('seaborn-v0_8')

ROOT_DIR = Path(__file__).resolve().parent.parent
HISTORY_PATH = ROOT_DIR / "data" / "history.csv"

wins = Counter()
games = Counter()
total_games_per_player = Counter()
all_players = set()

with HISTORY_PATH.open() as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 4:
            winner, loser, date, game = row
            # Clean up quotes introduced by CSV writing.
            winner = winner.strip('"')
            loser = loser.strip('"')
            game = game.strip('"')
            all_players.add(winner)
            all_players.add(loser)
            if winner != "Draw":
                wins[winner] += 1
                total_games_per_player[winner] += 1
                total_games_per_player[loser] += 1
            else:
                # Draw, both players played.
                total_games_per_player[winner] += 1  # winner is "Draw", but actually both
                total_games_per_player[loser] += 1
            games[game] += 1

# Create a figure with three subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Game Hub Statistics Dashboard', fontsize=16, fontweight='bold')

# Top 5 players by total wins (including those with 0 wins)
player_win_counts = [(player, wins.get(player, 0)) for player in all_players]
top5 = sorted(player_win_counts, key=lambda x: x[1], reverse=True)[:5]
if top5:
    names = [n for n, c in top5]
    win_counts = [c for n, c in top5]
    bars = ax1.bar(names, win_counts, color=plt.cm.viridis([0.2, 0.4, 0.6, 0.8, 1.0][:len(names)]))
    ax1.set_title("Top 5 Players by Wins", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Players", fontsize=12)
    ax1.set_ylabel("Number of Wins", fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    # Add value labels on bars
    for bar, count in zip(bars, win_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(count), 
                ha='center', va='bottom', fontweight='bold')

# Pie chart of most played games
if games:
    labels = list(games.keys())
    sizes = list(games.values())
    colors = plt.cm.Set3(range(len(labels)))
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                                       colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax2.set_title("Game Popularity Distribution", fontsize=14, fontweight='bold')
    ax2.axis('equal')
    # Improve text
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

# Top 5 players by total games played
top5_games = total_games_per_player.most_common(5)
if top5_games:
    names = [n for n, c in top5_games]
    game_counts = [c for n, c in top5_games]
    bars = ax3.bar(names, game_counts, color=plt.cm.plasma([0.2, 0.4, 0.6, 0.8, 1.0][:len(names)]))
    ax3.set_title("Top 5 Most Active Players", fontsize=14, fontweight='bold')
    ax3.set_xlabel("Players", fontsize=12)
    ax3.set_ylabel("Total Games Played", fontsize=12)
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    # Add value labels
    for bar, count in zip(bars, game_counts):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(count), 
                ha='center', va='bottom', fontweight='bold')

# Win rate chart for top players
win_rates = {}
for player in total_games_per_player:
    total = total_games_per_player[player]
    w = wins.get(player, 0)
    if total > 0:
        win_rates[player] = (w / total) * 100

top_win_rates = sorted(win_rates.items(), key=lambda x: x[1], reverse=True)[:5]
if top_win_rates:
    names = [n for n, r in top_win_rates]
    rates = [r for n, r in top_win_rates]
    bars = ax4.bar(names, rates, color=plt.cm.coolwarm([0.2, 0.4, 0.6, 0.8, 1.0][:len(names)]))
    ax4.set_title("Top 5 Players by Win Rate (%)", fontsize=14, fontweight='bold')
    ax4.set_xlabel("Players", fontsize=12)
    ax4.set_ylabel("Win Rate (%)", fontsize=12)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    ax4.set_ylim(0, 100)
    # Add value labels
    for bar, rate in zip(bars, rates):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{rate:.1f}%', 
                ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()