import pygame
import numpy as np
from UI.State import MenuState, GameState

class Renderer:
    def __init__(self, player1, player2, event_manager):
        self.event_manager = event_manager
        self.menu_state = MenuState(player1, player2, event_manager, on_start=self.go_to_game_state)
        self.current_game = self.menu_state

    def go_to_game_state(self):
        self.current_game = GameState(self.menu_state.players[0], self.menu_state.players[1], self.event_manager)

    def update(self):
        if self.current_game:
            self.current_game.update()

    def render(self, screen):
        if self.current_game:
            self.current_game.render(screen)
