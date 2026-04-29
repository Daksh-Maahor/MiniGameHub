import os
import sys
import pygame
import numpy as np
import datetime
import csv
import subprocess
from pathlib import Path

# setting the root directory for imports and file paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.Settings import *
HISTORY_PATH = ROOT_DIR / "data" / "history.csv"
LEADERBOARD_SCRIPT = ROOT_DIR / "leaderboard.sh"
CHART_SCRIPT = ROOT_DIR / "src" / "chart.py"
BG_PATH = ROOT_DIR / "finalbackground.png"

def _clean_player_name(name: str) -> str:
    """Remove non-printable and non-ASCII characters from player names."""
    cleaned = ''.join(ch for ch in name if ch.isprintable() and ord(ch) < 128)
    return cleaned.strip()

def show_intro(screen, bg):
    """Display the welcome splash screen until the user presses a key or clicks."""
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    prompt_font = pygame.font.SysFont("Arial", 32)

    title = title_font.render("Welcome to MiniGameHub", True, TEXT_COLOR)
    prompt = prompt_font.render("Press any key or click to continue", True, (210, 210, 210))

    alpha = 0
    fade = pygame.Surface((width, height), pygame.SRCALPHA)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        screen.blit(bg, (0, 0))
        fade.fill((0, 0, 0, max(0, 180 - alpha)))
        screen.blit(fade, (0, 0))
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 3))
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height // 2 + 40))
        pygame.display.flip()

        if alpha < 180:
            alpha += 4
        clock.tick(60)


def draw_button(screen, text, font, rect, base_color, hover_color, events):
    """Render a button and return True only when it is clicked."""
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

    # Border highlight (glow-ish).
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

def show_message(screen, font, text, duration=2000):
    """Show a simple status message for a short timeout."""
    width, height = screen.get_size()
    screen.fill((0, 0, 0))
    msg = font.render(text, True, (255, 255, 255))
    screen.blit(msg, (width//2 - msg.get_width()//2, height//2 - msg.get_height()//2))
    pygame.display.flip()
    pygame.time.wait(duration)


def show_menu(screen, font, bg):
    """Render the main menu and return the selected action key."""
    width, height = screen.get_size()

    # Fonts sized to window (avoid overlap with cards).
    title_font = pygame.font.SysFont("Arial", int(height * 0.075), bold=True)
    subtitle_font = pygame.font.SysFont("Arial", int(height * 0.028), bold=False)

    # Main translucent panel.
    panel_rect = pygame.Rect(int(width * 0.1), int(height * 0.12), int(width * 0.8), int(height * 0.78))
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surf.fill((8, 12, 30, 190))

    # Card layout: make everything square.
    gap_x = int(panel_rect.width * 0.035)
    gap_y = int(panel_rect.height * 0.045)
    header_h = int(panel_rect.height * 0.22)

    avail_w = panel_rect.width - 2 * gap_x
    avail_h = panel_rect.height - header_h - 2 * gap_y
    side = min(avail_w // 3, avail_h // 3)
    side = max(side, int(min(panel_rect.width, panel_rect.height) * 0.18))

    # Center the 3-column grid inside panel_rect.
    total_grid_w = 3 * side + 2 * gap_x
    start_x = panel_rect.x + (panel_rect.width - total_grid_w) // 2
    start_y = panel_rect.y + header_h

    # X positions for 3 columns.
    x0 = start_x
    x1 = start_x + side + gap_x
    x2 = start_x + 2 * (side + gap_x)

    # Y positions for 3 rows (top games, middle tools, bottom exit).
    y0 = start_y
    y1 = start_y + side + gap_y
    y2 = start_y + 2 * (side + gap_y)

    exit_rect = pygame.Rect(panel_rect.x + (panel_rect.width - side) // 2, y2, side, side)

    # Card fonts: based on side so text always fits.
    card_font_big = pygame.font.SysFont("Arial", max(18, int(side * 0.12)), bold=True)
    card_font_small = pygame.font.SysFont("Arial", max(16, int(side * 0.10)), bold=True)

    def draw_icon(icon_kind: str, area: pygame.Rect, accent: tuple[int, int, int]):
        """Draw simple outlined icons with no external assets."""
        pygame.draw.rect(screen, (0, 0, 0), area, border_radius=18)
        # inner area
        inset = int(min(area.w, area.h) * 0.12)
        a = pygame.Rect(area.x + inset, area.y + inset, area.w - 2 * inset, area.h - 2 * inset)

        cx, cy = a.center
        t = max(2, int(a.w * 0.06))

        if icon_kind == "connect4":
            for i in range(4):
                # Center the 4 columns visually (symmetric spacing).
                step_x = max(8, int(a.w * 0.18))
                x = int(a.centerx + (i - 1.5) * step_x)
                for j in range(3):
                    step_y = max(8, int(a.h * 0.22))
                    y = int(a.centery + (j - 1) * step_y)
                    pygame.draw.circle(screen, accent, (x, y), max(4, int(a.w * 0.04)), t)
            pygame.draw.rect(screen, accent, pygame.Rect(a.x, a.bottom - max(10, int(a.h * 0.18)), a.w, 4), border_radius=4)
        elif icon_kind == "othello":
            # Cleaner “two discs + flip” icon.
            r = max(8, int(min(a.w, a.h) * 0.22))
            left_c = (int(a.centerx - r * 0.55), int(a.centery + r * 0.08))
            right_c = (int(a.centerx + r * 0.55), int(a.centery - r * 0.05))

            # Dark disc
            pygame.draw.circle(screen, (15, 15, 15), left_c, r)
            pygame.draw.circle(screen, accent, left_c, r, t)

            # Light disc
            pygame.draw.circle(screen, (245, 245, 255), right_c, r)
            pygame.draw.circle(screen, accent, right_c, r, t)

            # Small flip arrow between them.
            mid_x = int((left_c[0] + right_c[0]) / 2)
            mid_y = int((left_c[1] + right_c[1]) / 2)
            pygame.draw.line(screen, accent, (mid_x - r // 2, mid_y), (mid_x + r // 2, mid_y), t)
            pygame.draw.polygon(
                screen,
                accent,
                [
                    (mid_x + r // 2, mid_y),
                    (mid_x + r // 2 - t * 3, mid_y - t * 2),
                    (mid_x + r // 2 - t * 3, mid_y + t * 2),
                ],
            )
        elif icon_kind == "tictactoe":
            # 3x3 grid + small X and O in opposite corners.
            cell = int(min(a.w, a.h) / 3)
            grid_w = cell * 3
            inset_x = a.centerx - grid_w // 2
            inset_y = a.centery - grid_w // 2
            gx0, gy0 = inset_x, inset_y

            for i in range(1, 3):
                x = gx0 + cell * i
                y = gy0 + cell * i
                pygame.draw.line(screen, accent, (x, gy0), (x, gy0 + 3 * cell), t)
                pygame.draw.line(screen, accent, (gx0, y), (gx0 + 3 * cell, y), t)

            # X in top-left cell
            x1 = (gx0 + int(cell * 0.28), gy0 + int(cell * 0.28))
            x2p = (gx0 + int(cell * 0.72), gy0 + int(cell * 0.72))
            pygame.draw.line(screen, accent, x1, x2p, t)
            pygame.draw.line(screen, accent, (x2p[0], x1[1]), (x1[0], x2p[1]), t)

            # O in bottom-right cell
            o_center = (gx0 + int(cell * 2.72), gy0 + int(cell * 2.72))
            r = max(6, int(cell * 0.20))
            pygame.draw.circle(screen, accent, o_center, r, t)
        elif icon_kind == "leaderboard":
            # Trophy
            base_y = a.bottom - int(a.h * 0.15)
            pygame.draw.rect(screen, accent, pygame.Rect(a.x + a.w * 0.35, base_y, a.w * 0.3, int(a.h * 0.08)), border_radius=6)
            pygame.draw.polygon(
                screen,
                accent,
                [
                    (a.centerx, a.top + int(a.h * 0.2)),
                    (int(a.left + a.w * 0.15), base_y),
                    (int(a.right - a.w * 0.15), base_y),
                ],
            )
            # handles
            pygame.draw.arc(screen, accent, a.inflate(-int(a.w * 0.35), int(a.h * 0.05)), 3.2, 6.0, t)
        elif icon_kind == "howtoplay":
            # Question mark bubble outline
            pygame.draw.circle(screen, accent, a.center, int(min(a.w, a.h) * 0.36), t)
            # A simple '?' as lines
            pygame.draw.arc(screen, accent, a.inflate(-int(a.w * 0.25), -int(a.h * 0.25)), 3.6, 6.2, t)
            pygame.draw.circle(screen, accent, (a.centerx, int(a.top + a.h * 0.65)), max(4, int(a.w * 0.03)), t)
        elif icon_kind == "exit":
            # Power icon
            pygame.draw.circle(screen, accent, (cx, cy), int(min(a.w, a.h) * 0.30), t)
            pygame.draw.line(screen, accent, (cx - t * 0.2, int(cy - a.h * 0.4)), (cx - t * 0.2, int(cy - a.h * 0.05)), t)
        else:
            pygame.draw.rect(screen, accent, a, t, border_radius=12)

    def draw_card(rect: pygame.Rect, choice_key: str, label: str, icon_kind: str,
                   base: tuple[int, int, int], hover: tuple[int, int, int], card_font_local):
        """Render a selectable menu card and return its choice key on click."""
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        corner_radius = max(16, int(side * 0.10))

        # Shadow
        shadow = rect.copy()
        shadow.x += 6
        shadow.y += 6
        pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=corner_radius)

        # Background
        pygame.draw.rect(screen, hover if hovered else base, rect, border_radius=corner_radius)
        pygame.draw.rect(
            screen,
            (255, 255, 255) if hovered else (20, 20, 20),
            rect,
            2,
            border_radius=corner_radius,
        )

        # Icon area (top part)
        icon_area = pygame.Rect(
            rect.x + int(side * 0.12),
            rect.y + int(side * 0.12),
            int(side * 0.76),
            int(side * 0.52),
        )
        draw_icon(icon_kind, icon_area, hover if hovered else base)

        # Label (bottom)
        txt = card_font_local.render(label, True, TEXT_COLOR)
        shadow_txt = card_font_local.render(label, True, (0, 0, 0))
        tx = rect.x + rect.w // 2 - txt.get_width() // 2
        ty = rect.y + rect.h - txt.get_height() - int(side * 0.10)
        screen.blit(shadow_txt, (tx + 2, ty + 2))
        screen.blit(txt, (tx, ty))

        # Hover glow ring
        if hovered:
            glow = rect.inflate(-10, -10)
            pygame.draw.rect(screen, hover, glow, 3, border_radius=corner_radius)
        if hovered:
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    pygame.time.delay(120)
                    return choice_key
        return None

    while True:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(bg, (0, 0))
        screen.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(screen, (90, 160, 255), panel_rect, 2, border_radius=22)
        pygame.draw.rect(screen, (20, 30, 60), panel_rect, 6, border_radius=22)

        # Header inside the header area (avoids overlap with cards).
        title = title_font.render("MINI GAE HUB", True, TEXT_COLOR)
        shadow = title_font.render("MINI GAE HUB", True, (0, 0, 0))
        title_x = width // 2 - title.get_width() // 2
        title_y = panel_rect.y + int(header_h * 0.15)
        screen.blit(shadow, (title_x + 4, title_y + 4))
        screen.blit(title, (title_x, title_y))

        subtitle = subtitle_font.render("Pick your mode and challenge your partner.", True, (220, 220, 220))
        screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, title_y + title.get_height() + int(header_h * 0.07)))

        # Cards (square)
        choice = None
        # Top row: games
        choice = draw_card(pygame.Rect(x0, y0, side, side), "connect4", "Connect4", "connect4",
                            (255, 80, 120), (255, 160, 190), card_font_big) or choice
        choice = draw_card(pygame.Rect(x1, y0, side, side), "othello", "Othello", "othello",
                            (80, 200, 255), (170, 240, 255), card_font_big) or choice
        choice = draw_card(pygame.Rect(x2, y0, side, side), "tictactoe", "TicTacToe", "tictactoe",
                            (255, 170, 60), (255, 220, 150), card_font_big) or choice

        # Second row: tools
        mid_base = (30, 60, 120)
        mid_hover = (80, 180, 255)
        choice = draw_card(pygame.Rect(x0, y1, side, side), "leaderboard", "Leaderboard", "leaderboard",
                            mid_base, mid_hover, card_font_small) or choice
        choice = draw_card(pygame.Rect(x2, y1, side, side), "howtoplay", "How to play", "howtoplay",
                            mid_base, mid_hover, card_font_small) or choice

        # Third row: exit (square + centered)
        choice = draw_card(exit_rect, "exit", "Exit", "exit",
                            (120, 20, 40), (255, 80, 120), card_font_small) or choice

        if choice:
            return choice

        pygame.display.flip()

def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Word-wrap `text` into a list of lines that fit within `max_width` pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _draw_mini_board_tictactoe(screen: pygame.Surface, rect: pygame.Rect):
    # Mini visual: 10x10 grid is dense, so we draw a 10x10 faint grid with a highlighted 5-in-row.
    # This is a "hint" illustration, not interactive gameplay.
    grid_color = (120, 170, 255)
    line_color = (70, 100, 160)
    pygame.draw.rect(screen, (0, 0, 0, 90), rect, border_radius=18)
    inner = rect.inflate(-14, -20)
    inner_w = inner.w
    inner_h = inner.h
    cell = min(inner_w, inner_h) // 10
    grid_w = cell * 10
    grid_h = cell * 10
    ox = inner.x + (inner_w - grid_w) // 2
    oy = inner.y + (inner_h - grid_h) // 2

    # Grid
    for i in range(11):
        x = ox + i * cell
        y = oy + i * cell
        pygame.draw.line(screen, line_color, (x, oy), (x, oy + grid_h), 1)
        pygame.draw.line(screen, line_color, (ox, y), (ox + grid_w, y), 1)

    # Highlight a horizontal 5-in-row (example).
    r = 4
    c0 = 2
    for k in range(5):
        rr = oy + r * cell + 2
        cc = ox + (c0 + k) * cell + 2
        pygame.draw.rect(screen, grid_color, pygame.Rect(cc, rr, cell - 4, cell - 4), border_radius=6)

    label = pygame.font.SysFont("Arial", 18, bold=True).render("Need 5 in a row", True, (220, 240, 255))
    screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.bottom - 16))


def _draw_mini_board_othello(screen: pygame.Surface, rect: pygame.Rect):
    pygame.draw.rect(screen, (0, 0, 0, 90), rect, border_radius=18)
    inner = rect.inflate(-14, -20)
    cell = min(inner.w, inner.h) // 8
    grid_w = cell * 8
    grid_h = cell * 8
    ox = inner.x + (inner.w - grid_w) // 2
    oy = inner.y + (inner.h - grid_h) // 2

    line_color = (90, 140, 110)
    for i in range(9):
        x = ox + i * cell
        y = oy + i * cell
        pygame.draw.line(screen, line_color, (x, oy), (x, oy + grid_h), 1)
        pygame.draw.line(screen, line_color, (ox, y), (ox + grid_w, y), 1)

    # Initial four discs.
    # Board center: (3,3)=White(2), (3,4)=Black(1), (4,3)=Black(1), (4,4)=White(2)
    def disc(r, c, color, border=None):
        cx = ox + c * cell + cell // 2
        cy = oy + r * cell + cell // 2
        radius = max(5, cell // 3)
        pygame.draw.circle(screen, color, (cx, cy), radius)
        if border is not None:
            pygame.draw.circle(screen, border, (cx, cy), radius, 3)

    disc(3, 3, (245, 245, 255), (80, 200, 255))
    disc(3, 4, (20, 20, 20), (255, 80, 120))
    disc(4, 3, (20, 20, 20), (255, 80, 120))
    disc(4, 4, (245, 245, 255), (80, 200, 255))

    label = pygame.font.SysFont("Arial", 18, bold=True).render("Flip trapped discs", True, (220, 255, 230))
    screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.bottom - 16))


def _draw_mini_board_connect4(screen: pygame.Surface, rect: pygame.Rect):
    pygame.draw.rect(screen, (0, 0, 0, 90), rect, border_radius=18)
    inner = rect.inflate(-14, -20)
    cell = min(inner.w // 7, inner.h // 7)
    grid_w = cell * 7
    grid_h = cell * 7
    ox = inner.x + (inner.w - grid_w) // 2
    oy = inner.y + (inner.h - grid_h) // 2

    # Board holes
    for r in range(7):
        for c in range(7):
            cx = ox + c * cell + cell // 2
            cy = oy + r * cell + cell // 2
            pygame.draw.circle(screen, (20, 20, 35), (cx, cy), max(6, cell // 3), 0)

    # Highlight a diagonal 4 (example).
    accent = (255, 80, 120)
    coords = [(6, 0), (5, 1), (4, 2), (3, 3)]
    for rr, cc in coords:
        cx = ox + cc * cell + cell // 2
        cy = oy + rr * cell + cell // 2
        pygame.draw.circle(screen, accent, (cx, cy), max(6, cell // 3))
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), max(6, cell // 3), 2)

    label = pygame.font.SysFont("Arial", 18, bold=True).render("Drop to align 4", True, (255, 230, 230))
    screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.bottom - 16))


def show_how_to_play(screen: pygame.Surface, bg: pygame.Surface):
    """Interactive How-To-Play screen with tabs and small illustrative boards."""
    width, height = screen.get_size()
    font_title = pygame.font.SysFont("Arial", int(height * 0.06), bold=True)
    font_body = pygame.font.SysFont("Arial", int(height * 0.022))
    font_small = pygame.font.SysFont("Arial", int(height * 0.018), bold=True)

    panel_rect = pygame.Rect(int(width * 0.08), int(height * 0.12), int(width * 0.84), int(height * 0.78))
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surf.fill((8, 12, 30, 200))

    tabs = [
        ("tictactoe", "TicTacToe"),
        ("othello", "Othello"),
        ("connect4", "Connect4"),
    ]
    tab_rects = []
    tab_y = panel_rect.y + int(panel_rect.height * 0.09)
    tab_w = int(panel_rect.w * 0.22)
    tab_h = int(panel_rect.h * 0.08)
    tab_gap = int(panel_rect.w * 0.03)
    start_tx = panel_rect.x + (panel_rect.w - (3 * tab_w + 2 * tab_gap)) // 2
    for i, (_, label) in enumerate(tabs):
        tab_rects.append(pygame.Rect(start_tx + i * (tab_w + tab_gap), tab_y, tab_w, tab_h))

    back_rect = pygame.Rect(panel_rect.x + int(panel_rect.w * 0.78), panel_rect.y + int(panel_rect.h * 0.89), int(panel_rect.w * 0.18), tab_h)

    selected = 0
    clock = pygame.time.Clock()
    while True:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for i, r in enumerate(tab_rects):
                    if r.collidepoint(mx, my):
                        selected = i
                if back_rect.collidepoint(mx, my):
                    return

        screen.blit(bg, (0, 0))
        screen.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(screen, (90, 160, 255), panel_rect, 2, border_radius=22)

        title = font_title.render("How to Play", True, TEXT_COLOR)
        shadow = font_title.render("How to Play", True, (0, 0, 0))
        tx = width // 2 - title.get_width() // 2
        ty = panel_rect.y + int(panel_rect.height * 0.03)
        screen.blit(shadow, (tx + 4, ty + 4))
        screen.blit(title, (tx, ty))

        # Tabs
        for i, (_, label) in enumerate(tabs):
            r = tab_rects[i]
            base = (30, 60, 120) if i != selected else (80, 180, 255)
            hover = (80, 180, 255) if i != selected else (170, 240, 255)
            hovered = r.collidepoint(pygame.mouse.get_pos())
            col = hover if hovered else base
            pygame.draw.rect(screen, (0, 0, 0, 80), r, border_radius=16)
            pygame.draw.rect(screen, col, r, border_radius=16)
            pygame.draw.rect(screen, (255, 255, 255) if i == selected else (20, 20, 20), r, 2, border_radius=16)
            t = font_small.render(label, True, TEXT_COLOR)
            screen.blit(t, (r.x + r.w // 2 - t.get_width() // 2, r.y + r.h // 2 - t.get_height() // 2))

        # Content
        content_rect = panel_rect.inflate(-40, -int(panel_rect.height * 0.16))
        content_rect.y = panel_rect.y + int(panel_rect.h * 0.22)
        content_rect.h = int(panel_rect.h * 0.60)

        left = pygame.Rect(content_rect.x, content_rect.y, int(content_rect.w * 0.58), content_rect.h)
        right = pygame.Rect(content_rect.right - int(content_rect.w * 0.42), content_rect.y, int(content_rect.w * 0.42), content_rect.h)

        pygame.draw.rect(screen, (0, 0, 0, 70), left, border_radius=20)
        pygame.draw.rect(screen, (0, 0, 0, 70), right, border_radius=20)

        # Board hint + text.
        if selected == 0:
            _draw_mini_board_tictactoe(screen, right)
            heading = "Tic-Tac-Toe (Expanded)"
            body = (
                "Grid: 10x10. You win by getting 5 marks in a row.\n"
                "Lines can be horizontal, vertical, or diagonal.\n\n"
                "Turn: Players alternate placing X or O on any empty cell.\n"
                "Controls: Click an empty cell."
            )
        elif selected == 1:
            _draw_mini_board_othello(screen, right)
            heading = "Othello (Reversi)"
            body = (
                "Grid: 8x8, starting with two Black and two White discs in the center.\n"
                "A move is valid only if it traps opponent discs in a straight line.\n"
                "All trapped discs flip to your color (multiple lines can flip).\n\n"
                "If you have no valid moves, your turn is skipped.\n"
                "Controls: Click a valid empty square."
            )
        else:
            _draw_mini_board_connect4(screen, right)
            heading = "Connect Four"
            body = (
                "Grid: vertical 7x7. Drop coins into columns.\n"
                "Coins fall to the lowest empty row in the chosen column.\n"
                "You win by making 4 coins in a row (horizontal, vertical, diagonal).\n"
                "If the board fills with no winner: Draw.\n\n"
                "Controls: Click a column."
            )

        head = font_small.render(heading, True, TEXT_COLOR)
        screen.blit(head, (left.x + 18, left.y + 14))

        # Body text with wrapping.
        max_w = left.w - 36
        y = left.y + 44
        for line in body.splitlines():
            if not line.strip():
                y += int(height * 0.008)
                continue
            for wrapped in _wrap_text(line, font_body, max_w):
                surf = font_body.render(wrapped, True, (230, 230, 230))
                screen.blit(surf, (left.x + 18, y))
                y += int(height * 0.028)

        # Back button
        pygame.draw.rect(screen, (20, 20, 20), back_rect, border_radius=16)
        hovered = back_rect.collidepoint(pygame.mouse.get_pos())
        col = (255, 80, 120) if hovered else (120, 20, 40)
        pygame.draw.rect(screen, col, back_rect, border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), back_rect, 2, border_radius=16)
        back_t = font_small.render("Back", True, TEXT_COLOR)
        screen.blit(back_t, (back_rect.x + back_rect.w // 2 - back_t.get_width() // 2, back_rect.y + back_rect.h // 2 - back_t.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

def show_leaderboard_menu(screen, font, bg):
    """Display leaderboard sort options and return the selected metric."""
    width, height = screen.get_size()
    button_width = int(SCREEN_WIDTH * 0.25)
    button_height = int(SCREEN_HEIGHT * 0.1)
    spacing = 20

    title_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.09), bold=True)
    subtitle_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.03))
    btn_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.05), bold=True)

    labels = ["Sort by Wins", "Sort by Losses", "Sort by Ratio", "Back"]
    button_rects = []
    current_y = int(height * 0.25)
    for label in labels:
        rect = pygame.Rect(width//2 - button_width//2, current_y, button_width, button_height)
        button_rects.append(rect)
        current_y += button_height + spacing

    colors = [(BUTTON_BASE, BUTTON_HOVER)] * 3 + [((120, 20, 40), (255, 80, 120))]

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(bg, (0, 0))

        title = title_font.render("LEADERBOARD", True, TEXT_COLOR)
        screen.blit(title, (width//2 - title.get_width()//2, int(height * 0.08)))
        subtitle = subtitle_font.render("Choose how to sort the leaderboard.", True, (220, 220, 220))
        screen.blit(subtitle, (width//2 - subtitle.get_width()//2, int(height * 0.18)))

        for rect, label, color_pair in zip(button_rects, labels, colors):
            if draw_button(screen, label, btn_font, rect, color_pair[0], color_pair[1], events):
                return label.lower().replace("sort by ", "").replace(" ", "")

        pygame.display.flip()

def show_continue_prompt(screen, font, bg):
    """Ask the user whether to play again or quit after a game ends."""
    width, height = screen.get_size()
    button_width = int(SCREEN_WIDTH * 0.25)
    button_height = int(SCREEN_HEIGHT * 0.1)
    spacing = 20

    title_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.09), bold=True)
    subtitle_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.03))
    btn_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.05), bold=True)

    labels = ["Play Again", "Quit"]
    button_rects = []
    current_y = int(height * 0.25)
    for label in labels:
        rect = pygame.Rect(width//2 - button_width//2, current_y, button_width, button_height)
        button_rects.append(rect)
        current_y += button_height + spacing

    colors = [(BUTTON_BASE, BUTTON_HOVER), ((120, 20, 40), (255, 80, 120))]

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

        screen.blit(bg, (0, 0))

        title = title_font.render("GAME OVER", True, TEXT_COLOR)
        screen.blit(title, (width//2 - title.get_width()//2, int(height * 0.08)))
        subtitle = subtitle_font.render("What would you like to do?", True, (220, 220, 220))
        screen.blit(subtitle, (width//2 - subtitle.get_width()//2, int(height * 0.18)))

        for rect, label, color_pair in zip(button_rects, labels, colors):
            if draw_button(screen, label, btn_font, rect, color_pair[0], color_pair[1], events):
                return label == "Play Again"

        pygame.display.flip()

def run_game(screen, game, bg, game_name):
    """Run one game loop, handle clicks, and record the final result."""
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    while True:
        screen.blit(bg, (0, 0))
        events = pygame.event.get()
        result = game.draw_screen(screen, events)
        if result == "menu":
            return False
        pygame.display.flip()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                game.handle_click(x, y)
                winner = game.check_win()
                if winner:
                    # Log to history.csv
                    date = str(datetime.date.today())
                    if winner == "Draw":
                        winner_name = "Draw"
                        loser_name = "Draw"
                    else:
                        winner_name = winner
                        loser_name = game.players[1] if winner == game.players[0] else game.players[0]
                    with HISTORY_PATH.open('a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([winner_name, loser_name, date, game_name])
                    # Re-draw once so the overlay is shown on the final board state.
                    screen.blit(bg, (0, 0))
                    game.draw_screen(screen, [])
                    pygame.display.flip()
                    show_result(screen, font, winner)
                    return True
        clock.tick(60)

def show_result(screen, font, winner):
    """Show the end-of-game result overlay and pause briefly."""
    width, height = screen.get_size()
    text = "Draw!" if winner == "Draw" else f"{winner} Wins!"
    final = font.render(text, True, TEXT_COLOR)
    sub = font.render("Returning to menu shortly...", True, (200, 200, 200))
    # Semi-transparent panel so the last board state remains visible.
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((8, 12, 30, 190))
    screen.blit(overlay, (0, 0))
    screen.blit(final, (width // 2 - final.get_width() // 2, height // 2 - 40))
    screen.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 + 20))
    pygame.display.flip()
    # Keep the window responsive during the countdown.
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 2200:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(20)


def game_main(player1, player2):
    """Entry point for the game GUI. Initializes Pygame and handles menu navigation."""
    player1 = _clean_player_name(player1)
    player2 = _clean_player_name(player2)
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    width, height = screen.get_size()
    pygame.display.set_caption("Mini Gae Hub")

    try:
        bg = pygame.image.load(str(BG_PATH)).convert()
    except pygame.error:
        # Fallback background (in case finalbackground.png isn't present).
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        top = (8, 12, 28)
        mid = (18, 24, 45)
        bottom = (8, 12, 30)
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)
            if t < 0.5:
                a = t / 0.5
                col = (
                    int(top[0] * (1 - a) + mid[0] * a),
                    int(top[1] * (1 - a) + mid[1] * a),
                    int(top[2] * (1 - a) + mid[2] * a),
                )
            else:
                a = (t - 0.5) / 0.5
                col = (
                    int(mid[0] * (1 - a) + bottom[0] * a),
                    int(mid[1] * (1 - a) + bottom[1] * a),
                    int(mid[2] * (1 - a) + bottom[2] * a),
                )
            pygame.draw.line(bg, col, (0, y), (SCREEN_WIDTH, y))

        # Subtle stars.
        rng = np.random.default_rng(0)
        for _ in range(120):
            x = int(rng.integers(0, SCREEN_WIDTH))
            y = int(rng.integers(0, SCREEN_HEIGHT))
            r = int(rng.integers(1, 3))
            pygame.draw.circle(bg, (220, 230, 255), (x, y), r)
    else:
        bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    show_intro(screen, bg)
    font = pygame.font.SysFont("Arial", 140)
    # Default leaderboard sorting metric for post-game results.
    leaderboard_metric = "wins"
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        choice = show_menu(screen, font, bg)
        played_game = False
        if choice == "connect4":
            from src.games.connect4 import Connect4
            game = Connect4(player1, player2)
            played_game = run_game(screen, game, bg, "Connect4")
        elif choice == "othello":
            from src.games.othello import Othello
            game = Othello(player1, player2)
            played_game = run_game(screen, game, bg, "Othello")
        elif choice == "tictactoe":
            from src.games.tictactoe import TicTacToe
            game = TicTacToe(player1, player2)
            played_game = run_game(screen, game, bg, "TicTacToe")
        elif choice == "leaderboard":
            sub_choice = show_leaderboard_menu(screen, font, bg)
            if sub_choice in ["wins", "losses", "ratio"]:
                leaderboard_metric = sub_choice
                subprocess.run([str(LEADERBOARD_SCRIPT), sub_choice])
                # Non-blocking: chart.py uses plt.show() which would otherwise freeze Pygame.
                subprocess.Popen([sys.executable, str(CHART_SCRIPT)])
            continue
        elif choice == "chart":
            show_message(screen, font, "Charting not yet available.")
            continue
        elif choice == "howtoplay":
            show_how_to_play(screen, bg)
            continue
        elif choice == "exit":
            pygame.quit()
            sys.exit()
        else:
            continue
        if played_game:
            subprocess.run([str(LEADERBOARD_SCRIPT), leaderboard_metric])
            # Non-blocking: chart.py uses plt.show() which would otherwise freeze Pygame.
            subprocess.Popen([sys.executable, str(CHART_SCRIPT)])
            if not show_continue_prompt(screen, font, bg):
                running = False
    pygame.quit()

def main():
    """Run the game when executed as a script with two player names."""
    if len(sys.argv) != 3:
        print("Usage: python3 game.py <player1> <player2>")
        sys.exit(1)

    game_main(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
