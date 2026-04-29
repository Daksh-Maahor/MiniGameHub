#!/bin/bash

# Leaderboard generator. This script reads `data/history.csv` and prints a
# summary table sorted by wins, losses, or win ratio.

SORT_BY=$1

if [ "$SORT_BY" == "wins" ]; then
    SORT_COL=3
elif [ "$SORT_BY" == "losses" ]; then
    SORT_COL=4
elif [ "$SORT_BY" == "ratio" ]; then
    SORT_COL=5
else
    echo "Invalid sort metric. Use wins, losses, or ratio."
    exit 1
fi

# Resolve script-relative paths so the leaderboard works when called from anywhere.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
HISTORY_PATH="$DIR/data/history.csv"

# Process history.csv
awk -F, '
{
    game = $4
    winner = $1
    loser = $2
    sub(/^"/, "", winner); sub(/"$/, "", winner)
    sub(/^"/, "", loser); sub(/"$/, "", loser)
    sub(/^"/, "", game); sub(/"$/, "", game)
    if (winner != "Draw") {
        wins[game, winner]++
        losses[game, loser]++
    }
}
END {
    for (key in wins) {
        split(key, k, SUBSEP)
        game = k[1]
        user = k[2]
        w = wins[game, user]
        l = losses[game, user]
        ratio = (l > 0) ? w / l : w
        printf "%s,%s,%d,%d,%.2f\n", game, user, w, l, ratio
    }
    for (key in losses) {
        split(key, k, SUBSEP)
        game = k[1]
        user = k[2]
        if (!( (game, user) in wins )) {
            w = 0
            l = losses[game, user]
            ratio = 0
            printf "%s,%s,%d,%d,%.2f\n", game, user, w, l, ratio
        }
    }
}
' "$HISTORY_PATH" | sort -t, -k1,1 -k${SORT_COL},${SORT_COL}nr | awk -F, '
BEGIN {
    prev_game = ""
}
{
    game = $1
    user = $2
    w = $3
    l = $4
    ratio = $5
    if (game != prev_game) {
        if (prev_game != "") print ""
        print "Game: " game
        print "User                Wins  Losses  Ratio"
        print "----------------------------------------"
        prev_game = game
    }
    printf "%-18s %4d  %4d  %5.2f\n", user, w, l, ratio
}
'
