import sys
import numpy as np
import pygame
from game import BoardGame

ROWS = 10
COLS = 10
CELL_SIZE = 70

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

class TicTacToe(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, ROWS, COLS)
    
    def handle_click(self, x, y):
        width, height = pygame.display.get_surface().get_size()
        board_width = COLS * CELL_SIZE
        board_height = ROWS * CELL_SIZE
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        col = (x - OFFSET_X) // CELL_SIZE
        row = (y - OFFSET_Y) // CELL_SIZE

        if not (0 <= row < ROWS and 0 <= col < COLS):
            return
        if self.board[row][col] != 0:
            return
        
        self.board[row][col] = self.current_turn + 1
        self.switch_turn()

    def draw_screen(self, screen):
        width, height = screen.get_size()
        board_width = COLS * CELL_SIZE
        board_height = ROWS * CELL_SIZE
        OFFSET_X = (width - board_width) // 2
        OFFSET_Y = height - board_height - 50
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_col = (mouse_x - OFFSET_X) // CELL_SIZE
        hover_row = (mouse_y - OFFSET_Y) // CELL_SIZE

        board_rect = pygame.Rect(OFFSET_X, OFFSET_Y, board_width, board_height)
        pygame.draw.rect(screen, (20, 20, 60), board_rect)

        for i in range(ROWS + 1):
            pygame.draw.line(screen, (100, 100, 160), (OFFSET_X, OFFSET_Y + i * CELL_SIZE), (OFFSET_X + board_width, OFFSET_Y + i * CELL_SIZE), 2)
        for j in range(COLS + 1):
            pygame.draw.line(screen, (100, 100, 160), (OFFSET_X + j * CELL_SIZE, OFFSET_Y), (OFFSET_X + j * CELL_SIZE, OFFSET_Y + board_height), 2)
        
        for r in range(ROWS):
            for c in range(COLS):
                cx = c * CELL_SIZE + CELL_SIZE / 2 + OFFSET_X
                cy = r * CELL_SIZE + CELL_SIZE / 2 + OFFSET_Y
                val = self.board[r][c]

                if val == 1:
                    offset = CELL_SIZE // 3
                    pygame.draw.line(screen, (255, 80, 120), (cx - offset, cy - offset), (cx + offset, cy + offset), 6)
                    pygame.draw.line(screen, (255, 80, 120), (cx + offset, cy - offset), (cx - offset, cy + offset), 6)
                elif val == 2:
                    pygame.draw.circle(screen, (80, 200, 255), (int(cx), int(cy)), CELL_SIZE // 3, 6)
                
                if (r == hover_row and c == hover_col and 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == 0):
                    preview_color = (255, 80, 120) if self.current_turn == 0 else (80, 200, 255)
                    if self.current_turn == 0:
                        offset = CELL_SIZE // 4
                        pygame.draw.line(screen, preview_color, (cx - offset, cy - offset), (cx + offset, cy + offset), 3)
                        pygame.draw.line(screen, preview_color, (cx + offset, cy - offset), (cx - offset, cy + offset), 3)
                    else:
                        pygame.draw.circle(screen, preview_color, (int(cx), int(cy)), CELL_SIZE // 4, 3)

        font = pygame.font.SysFont("Arial", 40)
        turn_text = f"{self.get_current_player()}'s Turn"
        turn_render = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_render, (width//2 - turn_render.get_width()//2, OFFSET_Y - 80))

        p1 = self.players[0]
        p2 = self.players[1]
        left_x = OFFSET_X - 250
        right_x = OFFSET_X + board_width + 250
        center_y = OFFSET_Y + board_height // 2
        
        pygame.draw.line(screen, (255, 80, 120), (left_x - 20, center_y - 70), (left_x + 20, center_y - 30), 6)
        pygame.draw.line(screen, (255, 80, 120), (left_x + 20, center_y - 70), (left_x - 20, center_y - 30), 6)
        txt1 = font.render(p1, True, (255, 255, 255))
        screen.blit(txt1, (left_x - txt1.get_width() // 2, center_y))
        
        pygame.draw.circle(screen, (80, 200, 255), (right_x, center_y - 50), 25, 5)
        txt2 = font.render(p2, True, (255, 255, 255))
        screen.blit(txt2, (right_x - txt2.get_width() // 2, center_y))

        btn_font = pygame.font.SysFont("Arial", 30)
        if draw_button(screen, "Back", pygame.Rect(20, 20, 150, 70), (60, 60, 120), (120, 120, 255), btn_font):
            return "menu"
        if draw_button(screen, "Exit", pygame.Rect(width - 170, 20, 150, 70), (120, 40, 60), (255, 80, 120), btn_font):
            pygame.quit()
            sys.exit()

    def check_win(self):
        b = self.board

        for p in [1, 2]:
            h = (b[:, :-4] == p) & (b[:, 1:-3] == p) & (b[:, 2:-2] == p) & (b[:, 3:-1] == p) & (b[:, 4:] == p)
            if np.any(h):
                return self.players[p - 1]
            v = (b[:-4, :] == p) & (b[1:-3, :] == p) & (b[2:-2, :] == p) & (b[3:-1, :] == p) & (b[4:, :] == p)
            if np.any(v):
                return self.players[p - 1]
            d1 = (b[:-4, :-4] == p) & (b[1:-3, 1:-3] == p) & (b[2:-2, 2:-2] == p) & (b[3:-1, 3:-1] == p) & (b[4:, 4:] == p)
            if np.any(d1):
                return self.players[p - 1]
            d2 = (b[4:, :-4] == p) & (b[3:-1, 1:-3] == p) & (b[2:-2, 2:-2] == p) & (b[1:-3, 3:-1] == p) & (b[:-4, 4:] == p)
            if np.any(d2):
                return self.players[p - 1]

        if np.all(b != 0):
            return "Draw"
        return None
