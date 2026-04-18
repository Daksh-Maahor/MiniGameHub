import sys
import numpy as np
import pygame
from game import BoardGame

ROWS = 7
COLS = 7
CELL_SIZE = 100

def draw_button(screen, text, rect, base_color, hover_color, font):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=15)
        if click[0]:
            pygame.time.delay(150)
            return True
    else:
        pygame.draw.rect(screen, base_color, rect, border_radius=15)

    txt = font.render(text, True, (255, 255, 255))
    screen.blit(txt, (rect.x + rect.width//2 - txt.get_width()//2, rect.y + rect.height//2 - txt.get_height()//2))
    return False

class Connect4(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, ROWS, COLS)

    def handle_click(self, x, y):
        width, height = pygame.display.get_surface().get_size()
        board_width = COLS * CELL_SIZE
        board_height = ROWS * CELL_SIZE
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        col = (x - OFFSET_X) // CELL_SIZE
        if col < 0 or col >= COLS:
            return

        column = self.board[:, col]
        empty = np.where(column == 0)[0]

        if len(empty) == 0:
            return
        row = empty[-1]

        self.board[row][col] = self.current_turn + 1
        self.switch_turn()

    def draw_screen(self, screen):
        width, height = screen.get_size()
        board_width = COLS * CELL_SIZE
        board_height = ROWS * CELL_SIZE
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        
        mouse_x, _ = pygame.mouse.get_pos()
        col = (mouse_x - OFFSET_X) // CELL_SIZE
        for r in range(ROWS):
            for c in range(COLS):
                pygame.draw.rect(screen, (20, 20, 60), (c * CELL_SIZE + OFFSET_X, r * CELL_SIZE + OFFSET_Y, CELL_SIZE, CELL_SIZE), border_radius=15)
                val = self.board[r][c]

                center = (c * CELL_SIZE + CELL_SIZE / 2 + OFFSET_X, r * CELL_SIZE + CELL_SIZE / 2 + OFFSET_Y)
                color = (10, 10, 20)
                if val == 1:
                    color = (255, 80, 120)
                elif val == 2:
                    color = (80, 200, 255)
                if val != 0:
                    pygame.draw.circle(screen, color, center, CELL_SIZE // 2.5)
                pygame.draw.circle(screen, color, center, CELL_SIZE // 3)

                if 0 <= col < COLS:
                    preview_color = (255, 80, 120) if self.current_turn == 0 else (80, 200, 255)
                    pygame.draw.circle(screen, preview_color, (int(col * CELL_SIZE + CELL_SIZE/2 + OFFSET_X), int(OFFSET_Y - 40)), int(CELL_SIZE / 3))
        
        font = pygame.font.SysFont("Arial", 40)
        p1 = self.players[0]
        p2 = self.players[1]
        p1_color = (255, 80, 120)
        p2_color = (80, 200, 255)

        left_x = OFFSET_X - 250
        right_x = OFFSET_X + board_width + 250
        center_y = OFFSET_Y + board_height // 2
        
        txt1 = font.render(p1, True, (255, 255, 255))
        pygame.draw.circle(screen, p1_color, (left_x, center_y - 50), CELL_SIZE // 2.5)
        screen.blit(txt1, (left_x - txt1.get_width() / 2, center_y))
        txt2 = font.render(p2, True, (255, 255, 255))
        pygame.draw.circle(screen, p2_color, (right_x, center_y - 50), CELL_SIZE // 2.5)
        screen.blit(txt2, (right_x - txt2.get_width() / 2, center_y))

        turn_text = f"{self.get_current_player()}'s Turn"
        turn_render = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_render, (width//2 - turn_render.get_width()//2, OFFSET_Y - 80))

        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), btn_font):
            return "menu"
        if draw_button(screen, "Exit", pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), btn_font):
            pygame.quit()
            sys.exit()

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
            d2 = (b[3:, :-3] == p) & (b[2:-1, 1:-2] == p) & (b[1:-2, 2:-1] == p) & (b[:-3, 3:] == p)
            if np.any(d2):
                return self.players[p - 1]
        
        if np.all(b != 0):
            return "Draw"

        return None