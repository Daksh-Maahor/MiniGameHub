import sys
from game import main as game_main


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 src/main.py <player1> <player2>")
        sys.exit(1)

    game_main()


if __name__ == "__main__":
    main()
