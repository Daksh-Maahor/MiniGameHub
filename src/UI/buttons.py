"""
Shared UI helpers for in-game screens.

This was originally stored as `src/ui.py`, but moved under `src/UI/` to keep
UI-related code grouped together.
"""

import pygame

from src.utils.Settings import TEXT_COLOR


def draw_button(screen, text, font, rect, base_color, hover_color, events) -> bool:
    """
    Draw a clickable button.

    Returns:
      True only if the user performs a left mouse click inside `rect`.
    """
    mouse = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse)

    corner_radius = 16

    # Drop shadow for depth.
    shadow_rect = rect.copy()
    shadow_rect.x += 4
    shadow_rect.y += 4
    pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=corner_radius)

    color = hover_color if hovered else base_color
    pygame.draw.rect(screen, color, rect, border_radius=corner_radius)

    # Border highlight.
    border_col = (255, 255, 255) if hovered else (20, 20, 20)
    pygame.draw.rect(screen, border_col, rect, 2, border_radius=corner_radius)

    txt = font.render(text, True, TEXT_COLOR)
    screen.blit(
        txt,
        (
            rect.x + rect.width // 2 - txt.get_width() // 2,
            rect.y + rect.height // 2 - txt.get_height() // 2,
        ),
    )

    if hovered:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pygame.time.delay(120)
                return True
    return False

