
from game.pybreakout import PyBreakout
import pygame

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("PyBreakout")

    game = PyBreakout()
    game.initializeScreen()
    game.play()


if __name__ == '__main__':
    main()


