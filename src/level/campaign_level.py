"""
    This is the campaign level or normal level that starts out with a certain number of sprites and
    is cleared when there are no more sprites to eliminate
"""

# Imports
import sys
import time
import random
import math
import pygame
import pygame.sprite
import pygame.mixer
import os
import glob
from pygame.locals import *

from .level import Level

from ..functions import *
from ..constants import *

from ..sprites.slime_blob import SlimeBlob, SLIME_RADIUS
from ..sprites.asteroid import Asteroid, ASTEROID_RADIUS
from ..sprites.cluster_asteroid import ClusterAsteroid, CLUSTER_ASTEROID_RADIUS

class CampaignLevel(Level):
    """Class representing a campaign level."""
    
    def __init__(self, number, screen_width, screen_height):
        self.level_number = number
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprites = pygame.sprite.Group()

        # TODO Possible change this to be a function instead of a property
        self.has_sprites_spawned = False
        
        self.has_gas_walls = False

        Level.__init__(self, number, screen_width, screen_height)
        
        self.sprite_count = (number-1) + BASE_LEVEL_SPRITE_COUNT
        self.generate_sprites()

    def get_asteroid_sprite_image(self):
        # TODO Refactor this
        suffixes = ["A", "B", "C", "D", "E", "F"]
        suff_index = (self.level_number-1) % len(suffixes)
        suff_char = suffixes[suff_index]
        return "sprites/asteroid_"+suff_char+".png"

    def generate_sprites(self):
        """Generates the objects or sprites used in the level."""
        if(self.has_gas_walls):
            self.genereate_gas_walls()
        
        for i in range(self.sprite_count):
            rand_val = random.randint(0, 10)
            
            if rand_val == 1:
                slimeblobs = 1

                if random.randint(1, 5) == 1:
                    slimeblobs = random.randint(2, 8)
                
                for i in range(slimeblobs):
                    self.sprites.add(self.generate_slime())
            elif rand_val == 2 and self.level_number >= 3:
                self.sprites.add(self.generate_cluster_asteroid())
            elif rand_val == 3:
                self.sprites.add(self.generate_large_asteroid())
            elif rand_val == 4:
                for i in range(4):
                    small_asteroid = self.generate_small_asteroid()
                    self.sprites.add(small_asteroid)
            else:
                self.sprites.add(self.generate_asteroid())

    def has_sprites(self):
        return not self.has_sprites_spawned

    def generate_asteroid(self):
        diameter = ASTEROID_RADIUS * 2
        ast_x, ast_y = self.generate_sprite_pos(diameter, diameter)
        
        asteroid = Asteroid(ast_x, ast_y, ASTEROID_RADIUS, self.get_asteroid_sprite_image())
        asteroid.set_angle(generate_angle())
        
        
        # Adds extra velocity after first level
        max_velocity = 150 + ((self.level_number-1) * 5)   
        asteroid.velocity = random.randint(50, max_velocity) / 100
        return asteroid

    def generate_small_asteroid(self):
        small_radius = ASTEROID_RADIUS//2
        diameter = small_radius * 2
        ast_x, ast_y = self.generate_sprite_pos(diameter, diameter)
        asteroid = Asteroid(ast_x, ast_y, small_radius, self.get_asteroid_sprite_image())
        asteroid.set_angle(generate_angle())
        

        # Adds extra velocity after first level
        max_velocity = 150 + ((self.level_number-1) * 5)   
        asteroid.velocity = random.randint(50, max_velocity) / 100
        asteroid.velocity *= 1.25
        asteroid.shatter_level = asteroid.shatter_level + 1
        return asteroid
    
    def generate_large_asteroid(self):
        large_radius = ASTEROID_RADIUS * 2
        diameter = large_radius * 2
        ast_x, ast_y = self.generate_sprite_pos(diameter, diameter)
                
        asteroid = Asteroid(ast_x, ast_y, large_radius, self.get_asteroid_sprite_image())

        asteroid.set_angle(generate_angle())
        max_velocity = 150 + ((self.level_number-1) * 5)   
        asteroid.velocity = (random.randint(50, max_velocity) / 100) * 0.75
        asteroid.max_shatter_level = asteroid.max_shatter_level +  1
        
        return asteroid
        
    def generate_cluster_asteroid(self):
        diameter = CLUSTER_ASTEROID_RADIUS * 2
        ast_x, ast_y = self.generate_sprite_pos(diameter, diameter)
        asteroid = ClusterAsteroid(ast_x, ast_y)
        asteroid.set_angle(generate_angle())
        

        # Adds extra velocity after first level
        max_velocity = 150 + ((self.level_number-1) * 5)   
        asteroid.velocity = random.randint(50, max_velocity) / 100
        return asteroid

        
    def generate_slime(self):
        diameter = SLIME_RADIUS * 2
        slime_x, slime_y = self.generate_sprite_pos(diameter, diameter)
        slimeblob = SlimeBlob(slime_x, slime_y)
        return slimeblob
    
    def generate_sprite_pos(self, width = 0, height = 0):
        x, y = -width//2, -height//2

        rand_val = random.randint(1, 4)

        if rand_val == 1:
            # Places the sprite on the left side.
            x = -width//2
            y = random.randint(0, WINDOWHEIGHT) - (-height//2)
        elif rand_val == 2:
            # Places the sprite on the top side.
            x = random.randint(0, WINDOWWIDTH) - (width//2)
            y = -height//2
        elif rand_val == 3:
            # Places the sprite on the right side.
            x = WINDOWWIDTH + (width//2)
            y = random.randint(0, WINDOWHEIGHT) - (-height//2)
        else:
            # Places the sprite on the bottom side.
            x = random.randint(0, WINDOWWIDTH) - (width//2)
            y = WINDOWHEIGHT + (height//2)
        
        return x, y
    
    def has_spawn_delay_elapsed(self):
        return self.spawn_time_ms < (get_millis() - self.spawn_delay_ms)
        
    
    def get_sprites(self):
        if not self.has_spawn_delay_elapsed():
            return []
        
        if not self.has_sprites_spawned:
            self.has_sprites_spawned = True
            return self.sprites
        else:
            return []
        
