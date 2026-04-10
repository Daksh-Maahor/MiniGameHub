import pygame
import numpy as np
from src.UI.State import State

class Renderer:
    def __init__(self, player1, player2, event_manager):
        self.menu_state = State(player1, player2, event_manager)

        self.current_game = self.menu_state

    def update(self):
        if self.current_game:
            self.current_game.update()

    def render(self, screen):
        if self.current_game:
            self.current_game.render(screen)
