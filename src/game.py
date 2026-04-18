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

def show_menu(screen, font, bg):
    width, height = screen.get_size()
    while True:
        screen.blit(bg, (0, 0))
        title = font.render("Game Hub", True, (255, 255, 255))
        screen.blit(title, (width//2 - title.get_width()//2, height//10))
        font1 = pygame.font.SysFont("Lora", 60)
        options=[
            "1-Connect4",
            "2-Othello",
            "3-TicTacToe",
            "Esc-Exit"
        ]
        for i in range (0,4):
            if (i != 3):
                op=font1.render(options[i], True, (0, 0, 255))
            else:
                op=font1.render(options[i], True, (255, 0, 0))
            screen.blit(op, (width//2 - op.get_width()//2, height//3 + i*80))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "connect4"
                elif event.key == pygame.K_2:
                    return "othello"
                elif event.key == pygame.K_3:
                    return "tictactoe"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def run_game(screen, game, bg):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    while True:
        screen.blit(bg, (0, 0))
        game.draw_screen(screen)
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
    bg = pygame.image.load("finalbackground.png")
    bg = pygame.transform.scale(bg, (width, height))
    show_intro(screen, bg)
    pygame.display.set_caption("Mini Game Hub")
    font = pygame.font.SysFont("Arial", 80)
    while True:
        choice = show_menu(screen, font, bg)
        if choice == "connect4":
            from games.connect4 import Connect4
            game = Connect4(player1, player2)
        elif choice == "othello":
            from games.othello import Othello
            game = Othello(player1, player2)
        elif choice == "tictactoe":
            from games.tictactoe import TicTacToe
            game = TicTacToe(player1, player2)
        else:
            continue

        run_game(screen, game, bg)


if __name__ == "__main__":
    main()
