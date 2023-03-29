import pygame
import pygame.sprite
from pygame.locals import *
import math
from ..constants import *
from .movable_sprite import MovableSprite


# Slimes
SLIME_RADIUS = 15
SLIME_COLOR = GREEN
SLIME_HP = 1
SLIME_SCORE = 25
SLIME_MAX_VELOCITY = 2
SLIME_ACC = 0.2

class SlimeBlob(MovableSprite):
    """An alien blob that will follow the player"""
    
    def __init__(self, x, y, radius = SLIME_RADIUS, color = SLIME_COLOR, sprite_image = "sprites/slime_blob_1.png"):
        self.radius = radius
        self.color = color
        self.score = SLIME_SCORE
        self.hp = SLIME_HP
        self.target_pos = (0, 0)
        self.max_velocity = SLIME_MAX_VELOCITY
        self.acc = SLIME_ACC

                
        diameter = self.radius*2
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        # Creates the slime's image.        
        self.image = pygame.Surface([diameter, diameter])
        self.image.set_colorkey(BACKGROUND_COLOR)                
        #pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)


        self.image = pygame.image.load(sprite_image).convert()
        self.image = pygame.transform.scale(self.image, (diameter, diameter))

        
        self.image.set_colorkey(BACKGROUND_COLOR)
        
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
        self.mask = pygame.mask.from_surface(self.image)

    def set_target(self, target_x, target_y):
        self.target_pos = (target_x, target_y)

    def rotate(self):
        # Sets angle based on the target position.
        target_x, target_y = self.target_pos

        slime_x, slime_y = self.x, self.y
        
        
        diff_x = target_x - slime_x 
        diff_y = target_y - slime_y

        distance = math.sqrt((diff_x**2)+(diff_y**2))

        if distance == 0:
            return # No need to change angle.
        
        angle = math.degrees(math.asin(diff_y/distance))

        if diff_x < 0:
           angle = 180 - angle 

        self.angle = angle

    def hit(self):
        self.hp -= 1

        if self.hp <= 0:
            self.kill()
            
        return self.score
