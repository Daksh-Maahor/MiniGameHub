# MINI GAME HUB
This project is created by and **Daksh Maahor (25B0974)** and **Rujul Garg (25B0937)**.

Mini Gae Hub is a two-player game launcher that uses Bash scripting for login/authentication and Pygame for the graphical game experience. Authenticated players can select a game, compete, and have their results persisted to a leaderboard.

## Requirements

- Python 3.11+ (or compatible)
- `pygame`
- `numpy`
- `matplotlib`

## Setup and Run

From the repository root:

```bash
bash main.sh
```

This script will:

- create a Python virtual environment under `venv/`
- install any missing Python packages
- create the data directory and persistence files under `data/`
- prompt both players to log in or register
- launch the Pygame hub once both players are authenticated

## Authentication

- User credentials are stored in `data/users.tsv`.
- Game results are stored in `data/history.csv`.
- Each username is hashed before storage so the raw password is never saved.

## Gameplay

Once the game hub opens, choose one of the available games:

- `Connect4`
- `Othello`
- `TicTacToe`

After a game finishes:

- the result is appended to `data/history.csv`
- `leaderboard.sh` is run to show the terminal leaderboard
- `src/chart.py` is launched to display charts

## Report

The `report/` folder contains the `main.tex` file containing the code for the Project Report.

To compile the report, from the `report/` folder run the command

```bash
make
```

## Notes

- The `data/` folder contains user and history files.
- Use only ASCII letters, digits, spaces, `.`, `_`, and `-` for usernames.
- If the game window cannot load the background image, it falls back to a generated gradient.

