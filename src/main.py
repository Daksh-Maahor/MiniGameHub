import sys
import pygame
from game import Renderer

class EventManager:
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.left_down = False

def main():
    pygame.init()
    WINDOW = pygame.display.set_mode((600,600))
    pygame.display.set_caption("Mini Gae Hub")
    clock = pygame.time.Clock()
    running = True

    event_manager = EventManager()

    renderer = Renderer(player1, player2, event_manager)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                event_manager.mouse_x, event_manager.mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                event_manager.left_down = True

        renderer.update()

        # render here

        renderer.render(WINDOW)

        # render above

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    player1 = sys.argv[1]
    player2 = sys.argv[2]
    main()
