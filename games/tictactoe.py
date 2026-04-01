import pygame
import numpy as np

class EventManager:
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.left_down = False

def main():
    pygame.init()

    SCREEN_SIZE = 720
    NUM_SQUARES = 10

    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("TicTacToe")
    clock = pygame.time.Clock()

    running = True

    # COLORS
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)

    event_manager = EventManager()

    board = np.full((NUM_SQUARES, NUM_SQUARES), -1)
    print(board)

    CURRENT_TURN = 1 # 1 : X, 0 : O, -1 : EMPTY

    while running:
        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                event_manager.mouse_x = pygame.mouse.get_pos()[0]
                event_manager.mouse_y = pygame.mouse.get_pos()[1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    event_manager.left_down = True

        # RENDER

        screen.fill(WHITE)

        # grid
        for i in range(1, NUM_SQUARES):
            pygame.draw.line(screen, BLACK, (SCREEN_SIZE * i // NUM_SQUARES,                              0), (SCREEN_SIZE * i // NUM_SQUARES,                    SCREEN_SIZE))
            pygame.draw.line(screen, BLACK, (                             0, SCREEN_SIZE * i // NUM_SQUARES), (                   SCREEN_SIZE, SCREEN_SIZE * i // NUM_SQUARES))
        
        if event_manager.left_down:
            x = event_manager.mouse_x // (SCREEN_SIZE // NUM_SQUARES)
            y = event_manager.mouse_y // (SCREEN_SIZE // NUM_SQUARES)
            board[y][x] = CURRENT_TURN
            event_manager.left_down = False

            print(board)
        
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    
    pygame.quit()

if __name__ == "__main__":
    main()
