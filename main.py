
from game.pybreakout import PyBreakout
import pygame
import src.main
import sys

def get_dump_flag():
    if 'dump' in sys.argv:
        return True
    return False

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("PyBreakout")

    game = PyBreakout(src.main.Entry())
    game.initializeScreen()
    game.setDump(get_dump_flag())
    game.play()


if __name__ == '__main__':
    main()


