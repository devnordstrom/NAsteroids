"""
MainGui controller that starts the game
"""
import pygame
import pygame.sprite
import pygame.mixer
import os
import glob
from .game import *
from .constants import *

class MainGui:

    def __init__(self):
        # Inits settings        
        self.init_gui()        

    def init_gui(self):
        # The extra pygame.mixer code is added in order to
        # make the sound effects play instantly.
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        # Inits pygame.
        pygame.init()
        
        self.windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption(CAPTION)
        pygame.mouse.set_visible(False)

    def start(self):
        """
            TODO Possibly display some sort of menu but for now
            just go ahead and get things started
        """

        game_mode = Game(self.windowSurface) 

        self.start_game(game_mode)

        # TODO add code for terminating Python
        
        pass

    def start_game(self, game_mode):
        print("Now starting game mode")

        game_mode.start()

        print("Now finished with game mode")
            

# Starts the program
# TODO Remove this, shouldn't be here
if __name__ == '__main__':
    mainGui = MainGui()
    mainGui.start()
