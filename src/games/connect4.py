import sys
import numpy as np
import pygame
from src.utils.Settings import *
from src.games.BoardGame import BoardGame
from src.UI.buttons import draw_button

ROWS = 7
COLS = 7

class Connect4(BoardGame):
    """Connect Four implementation on a 7x7 board."""

    def __init__(self, p1, p2):
        super().__init__(p1, p2, ROWS, COLS)
        self.cell_size = min(SCREEN_HEIGHT // (ROWS + 2), SCREEN_WIDTH // (COLS + 4))
        self.last_move_ts = None
        self.last_move_cell = None

    def handle_click(self, x, y):
        """Place a piece in the clicked column and advance the turn."""
        width, height = pygame.display.get_surface().get_size()
        board_width = COLS * self.cell_size
        board_height = ROWS * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        col = (x - OFFSET_X) // self.cell_size
        if col < 0 or col >= COLS:
            return

        column = self.board[:, col]
        empty = np.where(column == 0)[0]

        if len(empty) == 0:
            return
        row = empty[-1]

        self.board[row][col] = self.current_turn + 1
        self.last_move_ts = pygame.time.get_ticks()
        self.last_move_cell = (int(row), int(col))
        self.switch_turn()

    def draw_screen(self, screen, events):
        """Render the Connect4 board, pieces, hover preview, and buttons."""
        width, height = screen.get_size()
        board_width = COLS * self.cell_size
        board_height = ROWS * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        mouse_x, _ = pygame.mouse.get_pos()
        col = (mouse_x - OFFSET_X) // self.cell_size
        x_color = (255, 80, 120)
        o_color = (80, 200, 255)
        for r in range(ROWS):
            for c in range(COLS):
                cell_rect = pygame.Rect(
                    c * self.cell_size + OFFSET_X,
                    r * self.cell_size + OFFSET_Y,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(screen, (25, 25, 70), cell_rect, border_radius=15)
                pygame.draw.rect(screen, (90, 140, 255), cell_rect, 2, border_radius=15)
                val = self.board[r][c]

                center = (c * self.cell_size + self.cell_size / 2 + OFFSET_X, r * self.cell_size + self.cell_size / 2 + OFFSET_Y)
                color = (10, 10, 20)  # empty-hole color
                if val == 1:
                    color = x_color
                elif val == 2:
                    color = o_color
                if val != 0:
                    pygame.draw.circle(screen, color, center, self.cell_size // 2.5)
                    pygame.draw.circle(screen, color, center, self.cell_size // 2.5, 2)
                pygame.draw.circle(screen, color, center, self.cell_size // 3, 1)

                # Pulse ring on the last move to make the interaction feel snappier.
                if self.last_move_cell == (r, c) and self.last_move_ts is not None:
                    elapsed = pygame.time.get_ticks() - self.last_move_ts
                    if 0 <= elapsed <= 900:
                        t = 1.0 - (elapsed / 900.0)
                        ring_r = int(self.cell_size * (0.35 + 0.25 * t))
                        ring_w = max(1, int(4 * t))
                        pygame.draw.circle(screen, (220, 220, 255), center, ring_r, ring_w)

                if 0 <= col < COLS:
                    preview_color = (255, 80, 120) if self.current_turn == 0 else (80, 200, 255)
                    pygame.draw.circle(screen, preview_color, (int(col * self.cell_size + self.cell_size/2 + OFFSET_X), int(OFFSET_Y - 40)), int(self.cell_size / 3))
        
        font = pygame.font.SysFont("Arial", 40)
        p1 = self.players[0]
        p2 = self.players[1]
        p1_color = (255, 80, 120)
        p2_color = (80, 200, 255)

        left_x = OFFSET_X - 250
        right_x = OFFSET_X + board_width + 250
        center_y = OFFSET_Y + board_height // 2
        
        txt1 = font.render(p1, True, (255, 255, 255))
        pygame.draw.circle(screen, p1_color, (left_x, center_y - 50), self.cell_size // 2.5)
        screen.blit(txt1, (left_x - txt1.get_width() / 2, center_y))
        txt2 = font.render(p2, True, (255, 255, 255))
        pygame.draw.circle(screen, p2_color, (right_x, center_y - 50), self.cell_size // 2.5)
        screen.blit(txt2, (right_x - txt2.get_width() / 2, center_y))

        turn_text = f"{self.get_current_player()}'s Turn"
        turn_render = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_render, (width//2 - turn_render.get_width()//2, OFFSET_Y - 80))

        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", btn_font, pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), events):
            return "menu"
        if draw_button(screen, "Exit", btn_font, pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), events):
            pygame.quit()
            sys.exit()

    def check_win(self):
        """Check horizontal, vertical, and diagonal runs for a winner."""
        b = self.board

        h = (b[:, :-3] == 1) & (b[:, 1:-2] == 1) & (b[:, 2:-1] == 1) & (b[:, 3:] == 1)
        if np.any(h):
            return self.players[0]
        v = (b[:-3, :] == 1) & (b[1:-2, :] == 1) & (b[2:-1, :] == 1) & (b[3:, :] == 1)
        if np.any(v):
            return self.players[0]
        d1 = (b[:-3, :-3] == 1) & (b[1:-2, 1:-2] == 1) & (b[2:-1, 2:-1] == 1) & (b[3:, 3:] == 1)
        if np.any(d1):
            return self.players[0]
        d2 = (b[3:, :-3] == 1) & (b[2:-1, 1:-2] == 1) & (b[1:-2, 2:-1] == 1) & (b[:-3, 3:] == 1)
        if np.any(d2):
            return self.players[0]
        
        h = (b[:, :-3] == 2) & (b[:, 1:-2] == 2) & (b[:, 2:-1] == 2) & (b[:, 3:] == 2)
        if np.any(h):
            return self.players[1]
        v = (b[:-3, :] == 2) & (b[1:-2, :] == 2) & (b[2:-1, :] == 2) & (b[3:, :] == 2)
        if np.any(v):
            return self.players[1]
        d1 = (b[:-3, :-3] == 2) & (b[1:-2, 1:-2] == 2) & (b[2:-1, 2:-1] == 2) & (b[3:, 3:] == 2)
        if np.any(d1):
            return self.players[1]
        d2 = (b[3:, :-3] == 2) & (b[2:-1, 1:-2] == 2) & (b[1:-2, 2:-1] == 2) & (b[:-3, 3:] == 2)
        if np.any(d2):
            return self.players[1]

        if np.all(b != 0):
            return "Draw"

        return None