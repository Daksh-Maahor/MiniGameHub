import pygame
import numpy as np
from src.UI.State import State
from utils.Settings import SCREEN_SIZE, NUM_SQUARES

class TicTacToeState(State):
    def __init__(self, player1, player2):
        super().__init__(player1, player2)
        self.board = np.full((10, 10), -1) # 10x10 board
    
    def update(self):
        pass

    def render(self, screen):
        screen.fill((255, 255, 255)) # white background
        # grid
        for i in range(1, 10):
            pygame.draw.line(screen, (0, 0, 0), (SCREEN_SIZE * i // 10, 0), (SCREEN_SIZE * i // 10, SCREEN_SIZE)) # vertical lines
            pygame.draw.line(screen, (0, 0, 0), (0, SCREEN_SIZE * i // 10), (SCREEN_SIZE, SCREEN_SIZE * i // 10)) # horizontal lines

        if self.event_manager.left_down:
            x = self.event_manager.mouse_x // (SCREEN_SIZE // NUM_SQUARES)
            y = self.event_manager.mouse_y // (SCREEN_SIZE // NUM_SQUARES)
            self.board[y][x] = self.current_turn
            self.event_manager.left_down = False

            print(self.board)
        
        pygame.display.flip()
