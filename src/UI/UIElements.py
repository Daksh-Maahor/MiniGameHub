import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=(255, 255, 255), border_color=None, border_radius=20, onclick=None):
        self.rect = pygame.Rect(x, y, width, height)
        if onclick is None:
            onclick = lambda: None
        self.onclick = onclick
        self.text = text
        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.font = pygame.font.SysFont(None, 28, bold=True)

    def draw(self, screen, event_manager):
        shadow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 70), shadow.get_rect(), border_radius=self.border_radius)
        screen.blit(shadow, (self.rect.x + 4, self.rect.y + 4))

        if self.is_hovered(event_manager):
            color = (
                min(int(self.color[0] * 1.15), 255),
                min(int(self.color[1] * 1.15), 255),
                min(int(self.color[2] * 1.15), 255),
            )
        else:
            color = self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        if self.border_color is not None:
            pygame.draw.rect(screen, self.border_color, self.rect, width=2, border_radius=self.border_radius)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, event_manager):
        return self.rect.collidepoint(event_manager.mouse_x, event_manager.mouse_y)

    def is_clicked(self, event_manager):
        if event_manager.left_down and self.is_hovered(event_manager):
            event_manager.left_down = False
            if self.onclick is not None:
                self.onclick()
            return True
        return False
    
