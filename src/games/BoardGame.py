import numpy as np

class BoardGame:
    def __init__(self, player1, player2, rows, cols):
        self.players = [player1, player2]
        self.current_turn = 0
        self.board = np.zeros((rows, cols), dtype=int)

    def switch_turn(self):
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        return self.players[self.current_turn]