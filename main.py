import sys
import pygame

from Game import Renderer

def main():
    pygame.init()
    WINDOW = pygame.display.set_mode((600,600))
    pygame.display.set_caption("Mini Game Hub")
    clock = pygame.time.Clock()
    running = True

    renderer = Renderer(player1, player2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
