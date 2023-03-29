import pygame
from ..constants import *
from .movable_sprite import MovableSprite
from .asteroid import Asteroid

CLUSTER_ASTEROID_RADIUS = 100
CLUSTER_ASTEROID_SHATTER_LEVEL = 1
CLUSTER_ASTEROID_SHATTER_FACTOR = 2
CLUSTER_ASTEROID_SCORE = 50
CLUSTER_ASTEROID_HP = 1

class ClusterAsteroid(Asteroid):
    """Class representing Asteroids that can
        shatter into smaller asteroids on being hit"""

    def __init__(self, x, y, radius = CLUSTER_ASTEROID_RADIUS, sprite_image = "sprites/asteroid_cluster.png"):
        
        Asteroid.__init__(self, x, y, radius, sprite_image)
        
        self.max_shatter_level = CLUSTER_ASTEROID_SHATTER_LEVEL
        self.shatter_factor = CLUSTER_ASTEROID_SHATTER_FACTOR
        self.hp = CLUSTER_ASTEROID_HP
        self.score = CLUSTER_ASTEROID_SCORE
        self.split_velocity = self.velocity * 2
        self.enable_slime_spawning = False
        
    def get_split_asteroid_radius(self):
        return self.radius//4

    def split_asteroid(self, asteroids):
        
        asteroid = super().split_asteroid(asteroids)
        asteroid.velocity *= 2
        
        return asteroid
