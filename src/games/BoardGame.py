import numpy as np

"""Base class for grid-based board games used by each specific game mode."""

class BoardGame:
    def __init__(self, player1, player2, rows, cols):
        self.players = [player1, player2]
        # current_turn is 0 for players[0], 1 for players[1]
        self.current_turn = 0
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        # Optional UI hooks (set by individual games)
        self.last_move = None  # e.g., (r, c)
        self.win_cells = []   # list[(r, c)] for highlighting
        self.win_player = None

    def switch_turn(self):
        """Toggle the active player index between 0 and 1."""
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        """Return the current player's username."""
        return self.players[self.current_turn]

    def check_win(self):
        """
        Return:
          - a player name (winner),
          - "Draw",
          - or None if the game is still ongoing.
        """
        raise NotImplementedError