
from .. import constants
import pygame
import .movable_sprite

# Constants
METEROITE_COLOR = (222,184,135)
METEROITE_SCORE = 10
METEROITE_HP = 1

class Meteorite(MovableSprite):
    """Class representing a meteroite which may collide with the player but unlike the asteroid the meteroite will not shatter into smaller pieces or spawn slimes"""
    
    def __init__(self, x, y, radius):
        diameter = radius*2
        self.radius = radius
        self.color = METEROITE_COLOR
        
        
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        self.image = pygame.Surface([diameter, diameter])
        self.image.set_colorkey(constants.BACKGROUND_COLOR)                
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = METEROITE_HP
        self.score = METEROITE_SCORE

    def hit(self):
        self.hp -= 1

        if self.hp <= 0:
            self.kill()
            
        return self.score
