import os
import sys
import pygame
import numpy as np
import datetime
import csv
import subprocess
from pathlib import Path
from src.utils.Settings import *

ROOT_DIR = Path(__file__).resolve().parent
HISTORY_PATH = ROOT_DIR / "data" / "history.csv"
LEADERBOARD_SCRIPT = ROOT_DIR / "leaderboard.sh"
CHART_SCRIPT = ROOT_DIR / "chart.py"
BG_PATH = ROOT_DIR / "finalbackground.png"

def show_intro(screen, bg):
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    prompt_font = pygame.font.SysFont("Arial", 32)

    title = title_font.render("Welcome to MiniGaeHub", True, TEXT_COLOR)
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
    mouse = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse) else base_color
    pygame.draw.rect(screen, color, rect)
    txt = font.render(text, True, TEXT_COLOR)
    screen.blit(txt, (rect.x + rect.width // 2 - txt.get_width() // 2,
                      rect.y + rect.height // 2 - txt.get_height() // 2))
    if rect.collidepoint(mouse):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pygame.time.delay(120)
                return True
    return False

def show_message(screen, font, text, duration=2000):
    width, height = screen.get_size()
    screen.fill((0, 0, 0))
    msg = font.render(text, True, (255, 255, 255))
    screen.blit(msg, (width//2 - msg.get_width()//2, height//2 - msg.get_height()//2))
    pygame.display.flip()
    pygame.time.wait(duration)


def show_menu(screen, font, bg):
    width, height = screen.get_size()
    game_button_width = int(SCREEN_WIDTH * 0.25)
    game_button_height = int(SCREEN_HEIGHT * 0.1)
    small_button_width = int(SCREEN_WIDTH * 0.15)
    small_button_height = int(SCREEN_HEIGHT * 0.06)
    spacing = 20

    title_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.09), bold=True)
    subtitle_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.03))
    game_btn_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.05), bold=True)
    small_btn_font = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.035), bold=True)

    button_sizes = [(game_button_width, game_button_height)] * 3 + [(small_button_width, small_button_height)] * 4
    button_fonts = [game_btn_font] * 3 + [small_btn_font] * 4
    button_start_y = int(height * 0.25)
    button_rects = []
    current_y = button_start_y
    for size in button_sizes:
        rect = pygame.Rect(width//2 - size[0]//2, current_y, size[0], size[1])
        button_rects.append(rect)
        current_y += size[1] + spacing

    labels = ["Connect4", "Othello", "TicTacToe", "Leaderboard", "Chart", "How to Play", "Exit"]
    colors = [
        (BUTTON_BASE, BUTTON_HOVER),
        (BUTTON_BASE, BUTTON_HOVER),
        (BUTTON_BASE, BUTTON_HOVER),
        (SECONDARY_BASE, SECONDARY_HOVER),
        (SECONDARY_BASE, SECONDARY_HOVER),
        (SECONDARY_BASE, SECONDARY_HOVER),
        ((120, 20, 40), (255, 80, 120)),
    ]

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(bg, (0, 0))

        title = title_font.render("MINI GAE HUB", True, TEXT_COLOR)
        screen.blit(title, (width//2 - title.get_width()//2, int(height * 0.08)))
        subtitle = subtitle_font.render("Choose a game and play with your friends.", True, (220, 220, 220))
        screen.blit(subtitle, (width//2 - subtitle.get_width()//2, int(height * 0.18)))

        for rect, label, color_pair, btn_font in zip(button_rects, labels, colors, button_fonts):
            if draw_button(screen, label, btn_font, rect, color_pair[0], color_pair[1], events):
                return label.lower().replace(" ", "")

        pygame.display.flip()

def show_leaderboard_menu(screen, font, bg):
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
                    show_result(screen, font, winner)
                    return True
        clock.tick(60)

def show_result(screen, font, winner):
    width, height = screen.get_size()
    screen.fill((12, 16, 32))
    text = "Draw!" if winner == "Draw" else f"{winner} Wins!"
    final = font.render(text, True, TEXT_COLOR)
    sub = font.render("Returning to menu shortly...", True, (200, 200, 200))
    screen.blit(final, (width // 2 - final.get_width() // 2, height // 2 - 40))
    screen.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(2200)


def game_main(player1, player2):
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    width, height = screen.get_size()
    pygame.display.set_caption("Mini Gae Hub")

    try:
        bg = pygame.image.load(str(BG_PATH)).convert()
    except pygame.error:
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill(BACKGROUND_COLOR)
    else:
        bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    show_intro(screen, bg)
    font = pygame.font.SysFont("Arial", 140)
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
                subprocess.run([str(LEADERBOARD_SCRIPT), sub_choice])
                subprocess.Popen([sys.executable, str(CHART_SCRIPT)])
            continue
        elif choice == "chart":
            show_message(screen, font, "Charting not yet available.")
            continue
        elif choice == "howtoplay":
            show_message(screen, font, "Use mouse click to play Connect4.")
            continue
        elif choice == "exit":
            pygame.quit()
            sys.exit()
        else:
            continue
        if played_game:
            subprocess.run([str(LEADERBOARD_SCRIPT), "wins"])
            subprocess.Popen([sys.executable, str(CHART_SCRIPT)])
            if not show_continue_prompt(screen, font, bg):
                running = False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 game.py <player1> <player2>")
        sys.exit(1)

    game_main(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
