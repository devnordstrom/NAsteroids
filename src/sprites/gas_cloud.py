import pygame
from ..constants import *
from .movable_sprite import MovableSprite

GAS_CLOUD_COLOR = (150, 150, 150)
GAS_CLOUD_ALPHA = 150

class GasCloud(MovableSprite):

    def __init__(self, x, y, width, height):

        self.attractable = False
        self.temporary = True
        self.transparent = True
        self.toxic = True   # Means that the player will be killed upon touching this but other objects can pass it
        
        self.color = GAS_CLOUD_COLOR
        self.rect = Rect(x, y, width, height)
        self.image = pygame.Surface([width, height])
        self.image.set_colorkey(constants.BACKGROUND_COLOR)

        pygame.draw.rect(self.image, self.color, self.rect)

        self.image.set_alpha(GAS_CLOUD_ALPHA)
        
        MovableSprite.__init__(self, self.rect, self.image)

    def hit(self):
        return 0
