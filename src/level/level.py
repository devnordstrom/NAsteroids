"""
 The file contains the "abstract" Level class.
"""

# Imports
import sys
import time
import math
import pygame
import pygame.sprite
import pygame.mixer
import os
import glob
from pygame.locals import *

from ..functions import *
from ..constants import *

SPAWN_DELAY_MS = 3000

# Class definition(s)
class Level:
    """An "abstract" Class representing a level."""
    
    def __init__(self, number, screen_width, screen_height):
        self.level_number = number
        self.name = "Level: " + str(number);
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprites = pygame.sprite.Group()

        # TODO Possible change this to be a function instead of a property
        self.has_gas_walls = False

        self.spawn_time_ms = get_millis()
        self.spawn_delay_ms = SPAWN_DELAY_MS

    def is_cleared(self, sprite_group):
        """
            Evaluates if the level is cleared, normally this would be done by checking if the level still has asteroids/sprites
            however other types of level (Such as bonus levels) might simply be cleared automatically after a certain time or
            based on some other criteria.

            We supply all the sprites as an argument since the level itself doesn't handle this
        """
        
        if not self.has_spawn_delay_elapsed():
            return False

        if self.has_sprites():
            return False

        # Checks if there are still sprites in the level. This will not include bullets, ships or sprites that are "temporary" or " transparent"
        for sprite in sprite_group:
            if sprite.temporary or sprite.friendly:
                continue

            # Alright match found, this level isn't finished yet
            return False

        # The level is cleared
        return True

    def has_spawn_delay_elapsed(self):
        return self.spawn_time_ms < (get_millis() - self.spawn_delay_ms)
    
    def get_sprites(self):
        return []

    def has_sprites(self):
        return False

    def has_letal_walls(self):
        """
            This indicates weather or not the level will allow the spaceship
            to travel to the other side of the screen by crossing it or not.
        """
        return self.has_gas_walls
