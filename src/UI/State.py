import pygame

from src.UI.UIElements import Button
from src.utils.Colors import *

class State:
    def __init__(self, player1, player2, event_manager):
        self.players = [player1, player2]
        self.current_turn = 0
        self.event_manager = event_manager

    def update(self):
        pass

    def render(self, screen):
        pass

    def switch_turn(self):
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        return self.players[self.current_turn]

class MenuState(State):
    def __init__(self, player1, player2, event_manager, on_start=None):
        super().__init__(player1, player2, event_manager)
        self.title = "Mini Gae Hub"
        self.subtitle = "Classic board games with modern style"
        self.on_start = on_start or (lambda: None)
        self.buttons = []

        self.init_buttons()
    
    def init_buttons(self):
        button_width = 260
        button_height = 64
        x = 170
        y_start = 260
        spacing = 24

        labels = ["Start Game", "How to Play", "Quit"]
        actions = [self.on_start, lambda: print("How to Play clicked"), lambda: print("Quit clicked")]

        for index, label in enumerate(labels):
            y = y_start + index * (button_height + spacing)
            self.buttons.append(
                Button(
                    x,
                    y,
                    button_width,
                    button_height,
                    label,
                    BUTTON_BLUE,
                    text_color=WHITE,
                    border_color=BUTTON_BORDER,
                    onclick=actions[index]
                )
            )

    def update(self):
        for button in self.buttons:
            button.is_clicked(self.event_manager)

    def draw_background(self, screen):
        height = screen.get_height()
        width = screen.get_width()
        top = BACKGROUND_TOP
        bottom = BACKGROUND_BOTTOM

        for y in range(height):
            blend = y / (height - 1)
            color = (
                int(top[0] + (bottom[0] - top[0]) * blend),
                int(top[1] + (bottom[1] - top[1]) * blend),
                int(top[2] + (bottom[2] - top[2]) * blend),
            )
            pygame.draw.line(screen, color, (0, y), (width, y))

    def render(self, screen):
        self.draw_background(screen)

        panel = pygame.Surface((460, 360), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 180))
        pygame.draw.rect(panel, (255, 255, 255, 220), panel.get_rect(), border_radius=32)
        pygame.draw.rect(panel, (255, 255, 255, 120), panel.get_rect(), width=2, border_radius=32)
        screen.blit(panel, (70, 140))

        title_font = pygame.font.SysFont(None, 58, bold=True)
        subtitle_font = pygame.font.SysFont(None, 24)

        title_surface = title_font.render(self.title, True, WHITE)
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 200))
        screen.blit(title_surface, title_rect)

        subtitle_surface = subtitle_font.render(self.subtitle, True, LIGHT_TEXT)
        subtitle_rect = subtitle_surface.get_rect(center=(screen.get_width() / 2, 242))
        screen.blit(subtitle_surface, subtitle_rect)

        for button in self.buttons:
            button.draw(screen, self.event_manager)

class GameState(State):
    def __init__(self, player1, player2, event_manager):
        super().__init__(player1, player2, event_manager)
        self.title = "Game State"
        self.subtitle = "The game has started."

    def update(self):
        pass

    def render(self, screen):
        screen.fill(WHITE)
        title_font = pygame.font.SysFont(None, 48, bold=True)
        subtitle_font = pygame.font.SysFont(None, 24)

        title_surface = title_font.render(self.title, True, (18, 32, 67))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 20))
        screen.blit(title_surface, title_rect)

        subtitle_surface = subtitle_font.render(self.subtitle, True, (75, 82, 99))
        subtitle_rect = subtitle_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 20))
        screen.blit(subtitle_surface, subtitle_rect)
