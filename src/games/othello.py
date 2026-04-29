import numpy as np
import pygame
from src.games.BoardGame import BoardGame
from src.utils.Settings import *
from src.UI.buttons import draw_button

BOARD_SIZE = 8

class Othello(BoardGame):
    """Othello/Reversi implementation on an 8x8 board."""

    def __init__(self, p1, p2):
        super().__init__(p1, p2, BOARD_SIZE, BOARD_SIZE)
        self.cell_size = min(SCREEN_HEIGHT // (BOARD_SIZE + 2), SCREEN_WIDTH // (BOARD_SIZE + 4))
        # Initial board: center 4 squares
        self.board[3][3] = 2  # White
        self.board[3][4] = 1  # Black
        self.board[4][3] = 1  # Black
        self.board[4][4] = 2  # White
        self.last_move_ts = None
        self.last_move_cell = None

    def _shift(self, mask: np.ndarray, dr: int, dc: int) -> np.ndarray:
        """Shift a 2D boolean array with zero-padding to support vectorized direction scanning."""
        n = mask.shape[0]
        out = np.zeros_like(mask, dtype=bool)

        if dr >= 0:
            dst_r0, dst_r1 = dr, n
            src_r0, src_r1 = 0, n - dr
        else:
            dst_r0, dst_r1 = 0, n + dr
            src_r0, src_r1 = -dr, n

        if dc >= 0:
            dst_c0, dst_c1 = dc, n
            src_c0, src_c1 = 0, n - dc
        else:
            dst_c0, dst_c1 = 0, n + dc
            src_c0, src_c1 = -dc, n

        if dst_r0 >= dst_r1 or dst_c0 >= dst_c1:
            return out

        out[dst_r0:dst_r1, dst_c0:dst_c1] = mask[src_r0:src_r1, src_c0:src_c1]
        return out

    def get_valid_moves_mask(self, player: int) -> np.ndarray:
        """Compute a boolean mask of valid moves for the given player."""
        b = self.board
        opp = 3 - player
        P = (b == player)
        O = (b == opp)
        E = (b == 0)

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        valid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=bool)

        # For each direction, build up "opponent chain" starting from the adjacent cell.
        n = BOARD_SIZE
        for dr, dc in dirs:
            # chain[r,c] is True if the cell at (r,c) has an opponent disc one step away.
            chain = self._shift(O, -dr, -dc)  # opponent at pos1

            # k is the distance to the closing player's disc (k>=2).
            for k in range(2, n + 1):
                if k > 2:
                    # Require opponent discs all the way up to pos(k-1)
                    chain &= self._shift(O, -(k - 1) * dr, -(k - 1) * dc)
                valid |= chain & self._shift(P, -k * dr, -k * dc)

        return valid & E

    def is_valid_move(self, row, col, player):
        """Check whether a single board coordinate is a legal Othello move."""
        if self.board[row][col] != 0:
            return False
        opponent = 3 - player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE) or self.board[r][c] != opponent:
                continue
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opponent:
                r += dr
                c += dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                return True
        return False

    def place_and_flip(self, row, col, player):
        """Place a disc and flip all captured opponent discs in valid directions."""
        self.board[row][col] = player
        opponent = 3 - player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            to_flip = []
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opponent:
                to_flip.append((r, c))
                r += dr
                c += dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                for fr, fc in to_flip:
                    self.board[fr][fc] = player

    def has_valid_moves(self, player):
        """Check if the given player has any legal moves remaining."""
        return bool(np.any(self.get_valid_moves_mask(player)))

    def handle_click(self, x, y):
        """Handle a board click for Othello and apply the move if valid."""
        width, height = pygame.display.get_surface().get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        col = (x - OFFSET_X) // self.cell_size
        row = (y - OFFSET_Y) // self.cell_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            player = self.current_turn + 1
            if self.is_valid_move(row, col, player):
                self.place_and_flip(row, col, player)
                self.last_move_ts = pygame.time.get_ticks()
                self.last_move_cell = (int(row), int(col))
                self.switch_turn()
                # Skip if no moves
                while not self.has_valid_moves(self.current_turn + 1) and self.has_valid_moves(3 - (self.current_turn + 1)):
                    self.switch_turn()

    def draw_screen(self, screen, events):
        """Render the Othello board, valid-move hints, pieces, and controls."""
        width, height = screen.get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50

        current_player_mark = self.current_turn + 1
        valid_moves = self.get_valid_moves_mask(current_player_mark)
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell_rect = pygame.Rect(
                    c * self.cell_size + OFFSET_X,
                    r * self.cell_size + OFFSET_Y,
                    self.cell_size,
                    self.cell_size,
                )
                # Board look: dark "wood" tiles with neon edges.
                pygame.draw.rect(screen, (20, 50, 30), cell_rect, border_radius=10)
                pygame.draw.rect(screen, (80, 255, 170), cell_rect, 2, border_radius=10)

                if valid_moves[r, c] and self.board[r][c] == 0:
                    # Valid-move hint
                    center = (cell_rect.x + self.cell_size // 2, cell_rect.y + self.cell_size // 2)
                    elapsed = pygame.time.get_ticks()
                    pulse = 0.5 + 0.5 * np.sin(elapsed / 180.0)
                    rad = int(self.cell_size * (0.14 + 0.06 * pulse))
                    pygame.draw.circle(screen, (180, 255, 220), center, rad, 3)

                val = self.board[r][c]
                center = (c * self.cell_size + self.cell_size // 2 + OFFSET_X, r * self.cell_size + self.cell_size // 2 + OFFSET_Y)
                if val == 1:
                    pygame.draw.circle(screen, (20, 20, 20), center, self.cell_size // 2.5)  # Black
                    pygame.draw.circle(screen, (255, 80, 120), center, self.cell_size // 2.5, 2)
                elif val == 2:
                    pygame.draw.circle(screen, (240, 240, 255), center, self.cell_size // 2.5)  # White
                    pygame.draw.circle(screen, (80, 200, 255), center, self.cell_size // 2.5, 2)  # Glow border

                # Pulse ring on last move.
                if self.last_move_cell == (r, c) and self.last_move_ts is not None:
                    elapsed = pygame.time.get_ticks() - self.last_move_ts
                    if 0 <= elapsed <= 900:
                        t = 1.0 - (elapsed / 900.0)
                        ring_r = int(self.cell_size * (0.35 + 0.25 * t))
                        ring_w = max(1, int(4 * t))
                        pygame.draw.circle(screen, (220, 220, 255), center, ring_r, ring_w)
        
        font = pygame.font.SysFont("Arial", 40)
        p1 = self.players[0]  # Black
        p2 = self.players[1]  # White
        p1_color = (0, 0, 0)
        p2_color = (255, 255, 255)

        left_x = OFFSET_X - 250
        right_x = OFFSET_X + board_width + 250
        center_y = OFFSET_Y + board_height // 2
        
        txt1 = font.render(p1, True, (255, 255, 255))
        pygame.draw.circle(screen, p1_color, (left_x, center_y - 50), self.cell_size // 2.5)
        screen.blit(txt1, (left_x - txt1.get_width() // 2, center_y))
        txt2 = font.render(p2, True, (255, 255, 255))
        pygame.draw.circle(screen, p2_color, (right_x, center_y - 50), self.cell_size // 2.5)
        pygame.draw.circle(screen, (0, 0, 0), (right_x, center_y - 50), self.cell_size // 2.5, 2)
        screen.blit(txt2, (right_x - txt2.get_width() // 2, center_y))

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
        """Determine the winner by counting discs when the game ends."""
        # Game ends when neither player has a valid move, or when the board is full.
        b = self.board
        if np.all(b != 0) or (not self.has_valid_moves(1) and not self.has_valid_moves(2)):
            count1 = int(np.sum(b == 1))
            count2 = int(np.sum(b == 2))
            if count1 > count2:
                return self.players[0]
            if count2 > count1:
                return self.players[1]
            return "Draw"
        return None
