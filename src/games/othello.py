import numpy as np
import pygame
from src.games.BoardGame import BoardGame
from src.utils.Settings import *

BOARD_SIZE = 8

class Othello(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, BOARD_SIZE, BOARD_SIZE)
        self.cell_size = min(SCREEN_HEIGHT // (BOARD_SIZE + 2), SCREEN_WIDTH // (BOARD_SIZE + 4))
        # Initial board: center 4 squares
        self.board[3][3] = 2  # White
        self.board[3][4] = 1  # Black
        self.board[4][3] = 1  # Black
        self.board[4][4] = 2  # White

    def is_valid_move(self, row, col, player):
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
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c, player):
                    return True
        return False

    def handle_click(self, x, y):
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
                self.switch_turn()
                # Skip if no moves
                while not self.has_valid_moves(self.current_turn + 1) and self.has_valid_moves(3 - (self.current_turn + 1)):
                    self.switch_turn()

    def draw_screen(self, screen, events):
        width, height = screen.get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                pygame.draw.rect(screen, (0, 100, 0), (c * self.cell_size + OFFSET_X, r * self.cell_size + OFFSET_Y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, (0, 0, 0), (c * self.cell_size + OFFSET_X, r * self.cell_size + OFFSET_Y, self.cell_size, self.cell_size), 1)
                val = self.board[r][c]
                center = (c * self.cell_size + self.cell_size // 2 + OFFSET_X, r * self.cell_size + self.cell_size // 2 + OFFSET_Y)
                if val == 1:
                    pygame.draw.circle(screen, (0, 0, 0), center, self.cell_size // 2.5)  # Black
                elif val == 2:
                    pygame.draw.circle(screen, (255, 255, 255), center, self.cell_size // 2.5)  # White
                    pygame.draw.circle(screen, (0, 0, 0), center, self.cell_size // 2.5, 2)  # Border
        
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

        from src.game import draw_button
        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", btn_font, pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), events):
            return "menu"
        if draw_button(screen, "Exit", btn_font, pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), events):
            pygame.quit()
            import sys
            sys.exit()

    def check_win(self):
        if np.all(self.board != 0) or (not self.has_valid_moves(1) and not self.has_valid_moves(2)):
            count1 = np.sum(self.board == 1)
            count2 = np.sum(self.board == 2)
            if count1 > count2:
                return self.players[0]
            elif count2 > count1:
                return self.players[1]
            else:
                return "Draw"
        return None
