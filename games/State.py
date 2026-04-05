import pygame
import numpy as np

class State:
    # default is menu state
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.current_turn = 0

    def update(self):
        pass

    def render(self, screen):
        pass

    def switch_turn(self):
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        return self.players[self.current_turn]
    