import sys
import pygame
import numpy as np
from games.tictactoe import Connect4

class BoardGame:
    def __init__(self, player1, player2, rows, cols):
        self.players = [player1, player2]
        self.current_turn = 0
        self.board = np.zeros((rows, cols), dtype=int)

    def switch_turn(self):
        self.current_turn = 1 - self.current_turn

    def get_current_player(self):
        return self.players[self.current_turn]

def show_menu(screen,font):
    while True:
        screen.fill((0, 0, 0))
        title = font.render("Game Hub", True, (255, 255, 255))
        screen.blit(title, (220, 40))
        font = pygame.font.SysFont("Lora", 60)
        options=[
            "1-Connect4",
            "2-Othello",
            "3-TicTacToe",
            "Esc-Exit"
        ]
        for i in range (0,4):
            if (i != 3):
                op=font.render(options[i], True, (0, 0, 255))
            else:
                op=font.render(options[i], True, (255, 0, 0))
            screen.blit(op,(160, 160 + i*60))

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
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

def run_game(screen, game):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    while True:
        screen.fill((30, 30, 30))
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
    screen = pygame.display.set_mode((600,600))
    pygame.display.set_caption("Mini Game Hub")
    font = pygame.font.SysFont("Arial", 60)
    while True:
        choice = show_menu(screen, font)
        if choice == "connect4":
            game = Connect4(player1, player2)
        elif choice == "othello":
            from games.tictactoe import Othello
            game = Othello(player1, player2)
        elif choice == "tictactoe":
            from games.tictactoe import TicTacToe
            game = TicTacToe(player1, player2)
        else:
            continue

        run_game(screen, game)


if __name__ == "__main__":
    main()
