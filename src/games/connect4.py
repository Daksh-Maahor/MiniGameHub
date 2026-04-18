import numpy as np
import pygame
from game import BoardGame

ROWS = 7
COLS = 7
CELL_SIZE = 80

class Connect4(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, ROWS, COLS)

    def handle_click(self, x, y):
        col = x // CELL_SIZE
        if col >= COLS:
            return

        column = self.board[:, col]
        empty = np.where(column == 0)[0]

        if len(empty) == 0:
            return  
        row = empty[-1]

        self.board[row][col] = self.current_turn + 1
        self.switch_turn()

    def draw_screen(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                pygame.draw.rect(
                    screen,
                    (0, 0, 255),
                    (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
                val = self.board[r][c]

                center = (
                    c * CELL_SIZE + CELL_SIZE / 2,
                    r * CELL_SIZE + CELL_SIZE / 2
                )

                color = (0, 0, 0)
                if val == 1:
                    color = (255, 0, 0)  
                elif val == 2:
                    color = (255, 255, 0)

                pygame.draw.circle(screen, color, center, CELL_SIZE / 3)

    def check_win(self):
        b = self.board

        for p in [1,2]:
            h = (b[:, :-3] == p) & (b[:, 1:-2] == p) & (b[:, 2:-1] == p) & (b[:, 3:] == p)
            if np.any(h):
                return self.players[p - 1]
            v = (b[:-3, :] == p) & (b[1:-2, :] == p) & (b[2:-1, :] == p) & (b[3:, :] == p)
            if np.any(v):
                return self.players[p - 1]
            d1 = (b[:-3, :-3] == p) & (b[1:-2, 1:-2] == p) & (b[2:-1, 2:-1] == p) & (b[3:, 3:] == p)
            if np.any(d1):
                return self.players[p - 1]
            d1 = (b[3:, :-3] == p) & (b[2:-1, 1:-2] == p) & (b[1:-2, 2:-1] == p) & (b[:-3, 3:] == p)
            if np.any(d1):
                return self.players[p - 1]
        
        if np.all(b != 0):
            return "Draw"

        return None