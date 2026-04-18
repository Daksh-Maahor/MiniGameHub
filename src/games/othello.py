import sys
import numpy as np
import pygame
from game import BoardGame

ROWS = 8
COLS = 8
CELL_SIZE = 105

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

class Othello(BoardGame):
    def __init__(self, p1, p2):
        super().__init__(p1, p2, ROWS, COLS)

    def handle_click(self, x, y):

    def draw_screen(self, screen):

    def check_win(self):
