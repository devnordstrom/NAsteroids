import random
import pygame
from ..constants import *
from ..functions import generate_angle, load_image
from .movable_sprite import MovableSprite
from .vortex_hole import VortexHole
from .slime_blob import SlimeBlob

# Asteroid
ASTEROID_RADIUS = 50
ASTEROID_SHATTER_LEVEL = 2
ASTEROID_SHATTER_FACTOR = 2
ASTEROID_COLOR = (169,169,169)
ASTEROID_SCORE = 10
ASTEROID_HP = 1
ASTEROID_SPLIT_DOUBLE_CHANCE = 10
ASTEROID_SPAWN_SLIME_CHANCE = 7

class Asteroid(MovableSprite):
    """Class representing Asteroids that can
        shatter into smaller asteroids on being hit"""

    def __init__(self, x, y, radius = ASTEROID_RADIUS, sprite_image = "asteroid.png"):
        self.radius = radius
        self.sprite_image = sprite_image
        self.shatter_level = 1
        self.max_shatter_level = ASTEROID_SHATTER_LEVEL
        self.shatter_factor = ASTEROID_SHATTER_FACTOR
        self.should_split = True
        self.color = ASTEROID_COLOR
        self.score = ASTEROID_SCORE
        self.hp = ASTEROID_HP
        self.enable_slime_spawning = True
        
        diameter = self.radius*2
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        #self.image = pygame.image.load(sprite_image).convert()
        self.image = load_image(sprite_image)
        self.image = pygame.transform.scale(self.image, (diameter, diameter))
        self.image.set_colorkey(BACKGROUND_COLOR)
        
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
        #self.image = pygame.Surface([diameter, diameter])
        angle = random.randint(0, 360)
        self.set_angle(angle)

    def hit(self):
        self.hp -= 1

        if self.hp <= 0:
            self.kill()
            
        return self.score
        
    def split(self):
        
        # No need to split if the asteroid isn't destroyed or if
        # The asteroid isn't supposed to be split into smaller pieces.
        if self.shatter_level > self.max_shatter_level or self.hp > 0:
            return []
        
        # Checks if this should spawn a vortexhole
        #if self.shatter_level == 1 and random.randint(1,100) == 1:
        #    vortex_hole = self.spawn_vortex_hole()
        #   
        #   return [vortex_hole]
        
        occupied_angles = []
        sub_objects = []

        # Randomly spawns a slime blob.
        if self.enable_slime_spawning and random.randint(1, 100) <= ASTEROID_SPAWN_SLIME_CHANCE:
            sub_objects.append(self.spawn_slime())

        sub_ast_num = self.shatter_factor

        # Randomly creates twice as many sub asteroids.
        if random.randint(1, 100) <= ASTEROID_SPLIT_DOUBLE_CHANCE:
            sub_ast_num *= 2
        
        for n in range(sub_ast_num):
            asteroid = self.split_asteroid(occupied_angles)
            
            # Saves the new angle to prevent duplicate angles.
            occupied_angles.append(asteroid.angle)

            sub_objects.append(asteroid)
        
        return sub_objects

    def get_split_asteroid_radius(self):
        return self.radius//self.shatter_factor
    
    def split_asteroid(self, occupied_angles, image = None):

        # Changes to the current asteroids image
        # unless a specific one has been supplied.
        if image is None:
            image = self.sprite_image
        
        ast_x = self.rect.centerx
        ast_y = self.rect.centery

        ast_radius = self.get_split_asteroid_radius()
        
        asteroid = Asteroid(ast_x, ast_y, ast_radius, image)
        asteroid.shatter_level = self.shatter_level + 1
        asteroid.max_shatter_level = self.max_shatter_level
        asteroid.velocity = self.velocity

        ast_angle = generate_angle(occupied_angles)
        asteroid.set_angle(ast_angle)
        
        return asteroid

    def spawn_slime(self):
        """Spawns a slimeblob at the center of the asteroid"""
        ast_x = self.rect.centerx
        ast_y = self.rect.centery
        
        slime_blob = SlimeBlob(ast_x, ast_y)
        return slime_blob

    def spawn_vortex_hole(self):
        ast_x = self.rect.centerx
        ast_y = self.rect.centery

        vortex_hole = VortexHole(ast_x, ast_y)
        return vortex_hole
