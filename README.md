# MINI GAME HUB
This project is created by **Rujul-garg(25B0937)** and **Daksh-Maahor(25B0974)**.

We built a secure, multi-user game hub that integrates Bash scripting for authentication and Python(Pygame) for gameplay. Two authenticated players select a game from a menu, play via a graphical interface, and have their results recorded on a persistent leaderboard.

## How to Run

- Navigate to the project directory:  
`cd hub`

- Start the program:  
`bash main.sh`

## Usage

- Enter two usernames and passwords.
- Register if the user does not exist.
- Once both players are authenticated, call game.py with both usernames as command-line arguments:
`python3 game.py <username1> <username2>`

## Playing

- Select a game from the menu.
- Play using the GUI window.
- Results are saved automatically.

## After Each Game

- Leaderboard is shown in terminal.
- Graphs are displayed.
- Choose to play again or exit.

