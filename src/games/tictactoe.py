import numpy as np
import pygame
from src.games.BoardGame import BoardGame
from src.utils.Settings import *
from src.UI.buttons import draw_button
from numpy.lib.stride_tricks import sliding_window_view

BOARD_SIZE = 10

class TicTacToe(BoardGame):
    """Ten-by-ten TicTacToe implementation requiring five in a row to win."""

    def __init__(self, p1, p2):
        super().__init__(p1, p2, BOARD_SIZE, BOARD_SIZE)
        self.cell_size = min(SCREEN_HEIGHT // (BOARD_SIZE + 2), SCREEN_WIDTH // (BOARD_SIZE + 4))
        self.last_move_ts = None
        self.last_move_cell = None

    def _get_board_geometry(self):
        """Return consistent board geometry values for rendering and click handling."""
        width, height = pygame.display.get_surface().get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        offset_x = (width - board_width) // 2
        offset_y = height - board_height - 50
        return offset_x, offset_y, board_width, board_height

    def _get_hover_cell(self):
        """Return the current mouse hover cell if it falls within the board."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        offset_x, offset_y, board_width, board_height = self._get_board_geometry()
        col = (mouse_x - offset_x) // self.cell_size
        row = (mouse_y - offset_y) // self.cell_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return int(row), int(col)
        # Also allow exact-edge misses due to integer division:
        return None

    def handle_click(self, x, y):
        """Place a mark at the clicked cell and advance the turn."""
        OFFSET_X, OFFSET_Y, _, _ = self._get_board_geometry()
        col = (x - OFFSET_X) // self.cell_size
        row = (y - OFFSET_Y) // self.cell_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == 0:
            self.board[row][col] = self.current_turn + 1
            self.last_move_ts = pygame.time.get_ticks()
            self.last_move_cell = (int(row), int(col))
            self.win_cells = []
            self.switch_turn()

    def draw_screen(self, screen, events):
        """Render the TicTacToe grid, pieces, hover helper, and UI buttons."""
        width, height = screen.get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50

        hover_cell = self._get_hover_cell()
        win_set = set(self.win_cells)
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell_rect = pygame.Rect(
                    c * self.cell_size + OFFSET_X,
                    r * self.cell_size + OFFSET_Y,
                    self.cell_size,
                    self.cell_size,
                )
                # Board styling
                pygame.draw.rect(screen, (18, 32, 70), cell_rect, border_radius=10)
                pygame.draw.rect(screen, (90, 140, 255), cell_rect, 2, border_radius=10)

                val = self.board[r][c]
                center = (c * self.cell_size + self.cell_size // 2 + OFFSET_X, r * self.cell_size + self.cell_size // 2 + OFFSET_Y)
                x_color = (255, 80, 120)
                o_color = (80, 200, 255)
                dark_border = (0, 0, 0)

                if val == 1:
                    # X
                    thickness = 4
                    if (r, c) in win_set:
                        thickness = 6
                        pygame.draw.circle(screen, (180, 255, 120), center, self.cell_size // 3, 3)
                    pygame.draw.line(screen, x_color, (center[0] - self.cell_size // 3, center[1] - self.cell_size // 3), (center[0] + self.cell_size // 3, center[1] + self.cell_size // 3), thickness)
                    pygame.draw.line(screen, x_color, (center[0] + self.cell_size // 3, center[1] - self.cell_size // 3), (center[0] - self.cell_size // 3, center[1] + self.cell_size // 3), thickness)
                elif val == 2:
                    # O
                    radius = self.cell_size // 3
                    if (r, c) in win_set:
                        pygame.draw.circle(screen, (180, 255, 120), center, radius + 6, 4)
                    pygame.draw.circle(screen, o_color, center, radius, 4)
                    pygame.draw.circle(screen, dark_border, center, radius, 1)
                elif hover_cell == (r, c) and self.board[r][c] == 0:
                    # Hover hint for current player.
                    if self.current_turn == 0:
                        pygame.draw.line(screen, (255, 80, 120), (center[0] - self.cell_size // 8, center[1] - self.cell_size // 8), (center[0] + self.cell_size // 8, center[1] + self.cell_size // 8), 2)
                        pygame.draw.line(screen, (255, 80, 120), (center[0] + self.cell_size // 8, center[1] - self.cell_size // 8), (center[0] - self.cell_size // 8, center[1] + self.cell_size // 8), 2)
                    else:
                        pygame.draw.circle(screen, (80, 200, 255), center, self.cell_size // 8, 2)

                # Pulsing ring on the last move.
                if self.last_move_cell == (r, c) and self.last_move_ts is not None:
                    elapsed = pygame.time.get_ticks() - self.last_move_ts
                    if 0 <= elapsed <= 900:
                        t = 1.0 - (elapsed / 900.0)
                        ring_r = int(self.cell_size * (0.35 + 0.25 * t))
                        ring_w = max(1, int(4 * t))
                        pygame.draw.circle(
                            screen,
                            (220, 220, 255),
                            center,
                            ring_r,
                            ring_w,
                        )
        
        font = pygame.font.SysFont("Arial", 40)
        p1 = self.players[0]  # X
        p2 = self.players[1]  # O
        p1_color = (255, 80, 120)
        p2_color = (80, 200, 255)

        left_x = OFFSET_X - 250
        right_x = OFFSET_X + board_width + 250
        center_y = OFFSET_Y + board_height // 2
        
        txt1 = font.render(p1, True, (255, 255, 255))
        screen.blit(txt1, (left_x - txt1.get_width() // 2, center_y))
        # Draw X
        pygame.draw.line(screen, p1_color, (left_x - 20, center_y - 50 - 20), (left_x + 20, center_y - 50 + 20), 3)
        pygame.draw.line(screen, p1_color, (left_x + 20, center_y - 50 - 20), (left_x - 20, center_y - 50 + 20), 3)
        
        txt2 = font.render(p2, True, (255, 255, 255))
        screen.blit(txt2, (right_x - txt2.get_width() // 2, center_y))
        # Draw O
        pygame.draw.circle(screen, p2_color, (right_x, center_y - 50), 20, 3)

        turn_text = f"{self.get_current_player()}'s Turn"
        turn_render = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_render, (width // 2 - turn_render.get_width() // 2, OFFSET_Y - 80))

        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", btn_font, pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), events):
            return "menu"
        if draw_button(screen, "Exit", btn_font, pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), events):
            pygame.quit()
            import sys
            sys.exit()

    def check_win(self):
        """Check all directions for five in a row to determine the winner."""
        b = self.board
        n = BOARD_SIZE
        w = 5

        # Helper: returns list of 5 (r,c) cells if `mark` has a winning segment.
        def winning_cells_for_mark(mark: int):
            m = (b == mark)

            # Horizontal: shape (n, n-w+1, w)
            win_h = np.all(sliding_window_view(m, w, axis=1) == 1, axis=-1)
            if np.any(win_h):
                r, c = np.argwhere(win_h)[0]
                return [(int(r), int(cc)) for cc in range(int(c), int(c) + w)]

            # Vertical
            win_v = np.all(sliding_window_view(m, w, axis=0) == 1, axis=-1)
            if np.any(win_v):
                r, c = np.argwhere(win_v)[0]
                return [(int(rr), int(c)) for rr in range(int(r), int(r) + w)]

            starts = np.arange(n - w + 1)  # 0..5 for 10x10 with w=5
            k = np.arange(w)

            # Diagonal (top-left -> bottom-right)
            rows = starts[:, None, None] + k[None, None, :]
            cols = starts[None, :, None] + k[None, None, :]
            win_d1 = np.all(m[rows, cols] == 1, axis=-1)  # (6,6)
            if np.any(win_d1):
                r, c = np.argwhere(win_d1)[0]
                return [(int(r) + i, int(c) + i) for i in range(w)]

            # Anti-diagonal (top-right -> bottom-left)
            # Start column is in [w-1 .. n-1] => 4..9 for n=10, w=5 (6 positions)
            rows = starts[:, None, None] + k[None, None, :]
            cols = (starts[None, :, None] + (w - 1)) - k[None, None, :]
            win_d2 = np.all(m[rows, cols] == 1, axis=-1)  # (6,6)
            if np.any(win_d2):
                r, c = np.argwhere(win_d2)[0]
                start_col = int(c) + (w - 1)
                return [(int(r) + i, start_col - i) for i in range(w)]

            return []

        # Clear any previous highlight.
        self.win_cells = []

        for mark, player_idx in [(1, 0), (2, 1)]:
            cells = winning_cells_for_mark(mark)
            if cells:
                self.win_cells = cells
                self.win_player = mark
                return self.players[player_idx]

        if np.all(b != 0):
            return "Draw"
        return None
