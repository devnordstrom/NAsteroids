import math
import pygame
import pygame.sprite
from pygame.locals import *

from .. functions import get_millis
from ..constants import *
from .movable_sprite import MovableSprite

# Constants
BULLET_RADIUS = 4
BULLET_VELOCITY = 12
BULLET_DURATION_MS = 500
BULLET_COLOR = RED

class Bullet(MovableSprite):
    """Class representing bullet fired."""
    
    def __init__(self, left = 0, top = 0, radius = BULLET_RADIUS, bullet_color = BULLET_COLOR):
        self.radius = radius
        diameter = self.radius * 2
        self.color = bullet_color
        self.rect = Rect(left, top, diameter, diameter)

        self.image = pygame.Surface([diameter, diameter])
        self.image.set_colorkey(BACKGROUND_COLOR)                
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
                
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)

        self.mask = pygame.mask.from_surface(self.image)
        
        self.shot_time = 0
        self.shot_duration = BULLET_DURATION_MS
        self.parent = None
        self.temporary = True
        self.friendly = True
        
    def fire(self, angle, velocity = BULLET_VELOCITY):
        self.set_angle(angle)
        self.velocity = BULLET_VELOCITY
        self.shot_time = get_millis()

    def update(self):
        if self.shot_time > 0 and (get_millis() - self.shot_time) >= self.shot_duration:
            self.kill()
            return
        
        # Call parent function
        MovableSprite.update(self)
