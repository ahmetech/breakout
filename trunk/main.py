
from game.pybreakout import PyBreakout
import pygame
import src.main

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("PyBreakout")

    game = PyBreakout(src.main.Entry())
    game.initializeScreen()
    game.play()


if __name__ == '__main__':
    main()


