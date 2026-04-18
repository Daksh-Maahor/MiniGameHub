import sys
import pygame
import numpy as np

class BoardGame:
    def __init__(self, player1, player2, rows, cols):
        self.players = [player1, player2]
        self.current_turn = 0
        self.board = np.zeros((rows, cols), dtype=int)

    def switch_turn(self):
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        return self.players[self.current_turn]

def show_intro(screen, bg):
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    font_big = pygame.font.SysFont("Arial", 100)
    font_small = pygame.font.SysFont("Arial", 40)

    title = font_big.render("Welcome To The Pantheon", True, (255, 255, 255))
    prompt = font_small.render("Press any key to start", True, (200, 200, 200))

    alpha = 0
    running = True
    while running:
        screen.blit(bg, (0, 0))
        fade = pygame.Surface((width, height))
        fade.fill((0, 0, 0))
        fade.set_alpha(255 - alpha)
        screen.blit(fade, (0, 0))
        screen.blit(title, (width//2 - title.get_width()//2, height//3))
        screen.blit(prompt, (width//2 - prompt.get_width()//2, height//2))
        pygame.display.flip()

        if alpha < 255:
            alpha += 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        clock.tick(60)


def draw_button(screen, text, font, rect, base_color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if rect.collidepoint(mouse):
        glow_rect = rect.inflate(20, 20)
        pygame.draw.rect(screen, hover_color, glow_rect, border_radius=30)
        if click[0]:
            pygame.time.delay(200)
            return True
    else:
        pygame.draw.rect(screen, base_color, rect, border_radius=25)

    txt = font.render(text, True, (255, 255, 255))
    screen.blit(txt, (rect.x + rect.width//2 - txt.get_width()//2, rect.y + rect.height//2 - txt.get_height()//2))
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
    title_font = pygame.font.SysFont("Arial", 140)
    btn_font = pygame.font.SysFont("Lora", 50)

    while True:
        screen.blit(bg, (0, 0))
        title = title_font.render("GAME HUB", True, (255, 255, 255))
        screen.blit(title, (width//2 - title.get_width()//2, height//10))
        start_y = height // 3
        gap = 80
        
        if draw_button(screen, "Connect4", btn_font, pygame.Rect(width//2 - 200, start_y, 400, 60),(60, 30, 140), (140, 80, 255)):
            return "connect4"
        if draw_button(screen, "Othello", btn_font, pygame.Rect(width//2 - 200, start_y + gap, 400, 60),(60, 30, 140), (140, 80, 255)):
            return "othello"
        if draw_button(screen, "TicTacToe", btn_font, pygame.Rect(width//2 - 200, start_y + 2*gap, 400, 60),(60, 30, 140), (140, 80, 255)):
            return "tictactoe"
        if draw_button(screen, "Leaderboard", btn_font, pygame.Rect(width//2 - 200, start_y + 3*gap, 400, 60), (30, 60, 120), (80, 180, 255)):
            return "leaderboard"
        if draw_button(screen, "Chart", btn_font, pygame.Rect(width//2 - 200, start_y + 4*gap, 400, 60), (30, 60, 120), (80, 180, 255)):
            return "chart"
        if draw_button(screen, "How to Play", btn_font, pygame.Rect(width//2 - 200, start_y + 5*gap, 400, 60), (30, 60, 120), (80, 180, 255)):
            return "howtoplay"
        if draw_button(screen, "Exit", btn_font, pygame.Rect(width//2 - 200, start_y + 6*gap, 400, 60), (120, 20, 40), (255, 80, 120)):
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def run_game(screen, game, bg):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    while True:
        screen.blit(bg, (0, 0))
        result = game.draw_screen(screen)
        if result == "menu":
            return
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                game.handle_click(x, y)
                winner = game.check_win()
                if winner:
                    show_result(screen, font, winner)
                    return
        clock.tick(60)

def show_result(screen, font, winner):
    screen.fill((0, 0, 0))
    text = "Draw!" if winner == "Draw" else f"{winner} Wins!"
    final = font.render(text, True, (255, 255, 255))
    screen.blit(final, (200, 250))
    pygame.display.flip()
    pygame.time.wait(4000)

def main():
    player1 = sys.argv[1]
    player2 = sys.argv[2]
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    width, height = screen.get_size()
    bg = pygame.image.load("../finalbackground.png")
    bg = pygame.transform.scale(bg, (width, height))
    show_intro(screen, bg)
    pygame.display.set_caption("Mini Game Hub")
    font = pygame.font.SysFont("Arial", 140)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        choice = show_menu(screen, font, bg)
        if choice == "connect4":
            from games.connect4 import Connect4
            game = Connect4(player1, player2)
            run_game(screen, game, bg)
        elif choice == "othello":
            show_message(screen, font, "Othello is coming soon!")
            continue
        elif choice == "tictactoe":
            show_message(screen, font, "TicTacToe is coming soon!")
            continue
        elif choice == "leaderboard":
            show_message(screen, font, "Leaderboard not yet implemented.")
            continue
        elif choice == "chart":
            show_message(screen, font, "Charting not yet available.")
            continue
        elif choice == "howtoplay":
            show_message(screen, font, "Use mouse click to play Connect4.")
            continue
        else:
            continue
