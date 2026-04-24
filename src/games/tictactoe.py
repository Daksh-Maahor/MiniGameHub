import numpy as np
import pygame
from src.games.BoardGame import BoardGame
from src.utils.Settings import *

BOARD_SIZE = 10

class TicTacToe(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, BOARD_SIZE, BOARD_SIZE)
        self.cell_size = min(SCREEN_HEIGHT // (BOARD_SIZE + 2), SCREEN_WIDTH // (BOARD_SIZE + 4))

    def handle_click(self, x, y):
        width, height = pygame.display.get_surface().get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        col = (x - OFFSET_X) // self.cell_size
        row = (y - OFFSET_Y) // self.cell_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == 0:
            self.board[row][col] = self.current_turn + 1
            self.switch_turn()

    def draw_screen(self, screen, events):
        width, height = screen.get_size()
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                pygame.draw.rect(screen, (255, 255, 255), (c * self.cell_size + OFFSET_X, r * self.cell_size + OFFSET_Y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, (0, 0, 0), (c * self.cell_size + OFFSET_X, r * self.cell_size + OFFSET_Y, self.cell_size, self.cell_size), 1)
                val = self.board[r][c]
                center = (c * self.cell_size + self.cell_size // 2 + OFFSET_X, r * self.cell_size + self.cell_size // 2 + OFFSET_Y)
                if val == 1:
                    # X
                    pygame.draw.line(screen, (0, 0, 0), (center[0] - self.cell_size // 4, center[1] - self.cell_size // 4), (center[0] + self.cell_size // 4, center[1] + self.cell_size // 4), 3)
                    pygame.draw.line(screen, (0, 0, 0), (center[0] + self.cell_size // 4, center[1] - self.cell_size // 4), (center[0] - self.cell_size // 4, center[1] + self.cell_size // 4), 3)
                elif val == 2:
                    # O
                    pygame.draw.circle(screen, (0, 0, 0), center, self.cell_size // 3, 3)
        
        font = pygame.font.SysFont("Arial", 40)
        p1 = self.players[0]  # X
        p2 = self.players[1]  # O
        p1_color = (0, 0, 0)
        p2_color = (0, 0, 0)

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

        from src.game import draw_button
        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", btn_font, pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), events):
            return "menu"
        if draw_button(screen, "Exit", btn_font, pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), events):
            pygame.quit()
            import sys
            sys.exit()

    def check_win(self):
        def check_line(r, c, dr, dc, player):
            count = 0
            for i in range(5):
                nr, nc = r + i * dr, c + i * dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == player:
                    count += 1
                else:
                    break
            return count == 5
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                player = self.board[r][c]
                if player != 0:
                    # Check all directions
                    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    for dr, dc in directions:
                        if check_line(r, c, dr, dc, player):
                            return self.players[player - 1]
        if np.all(self.board != 0):
            return "Draw"
        return None
