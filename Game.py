import pygame
import numpy as np
from games.State import State

class Renderer:
    def __init__(self, player1, player2):
        self.game_smth = State(player1, player2)

        self.current_game = self.game_smth

    def update(self):
        if self.current_game:
            self.current_game.update()

    def render(self, screen):
        if self.current_game:
            self.current_game.render(screen)
