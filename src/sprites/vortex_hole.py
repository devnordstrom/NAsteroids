import pygame
from ..constants import *
from .movable_sprite import MovableSprite

# Constants
VORTEX_HOLE_RADIUS = 20
VORTEX_HOLE_SCORE = 50
VORTEX_HOLE_HP = 1
VORTEX_HOLE_ATTRACT_RADIUS = 300
VORTEX_HOLE_ATTRACT_ACC = -4
VORTEX_HOLE_COLOR = SNOT_GREEN

class VortexHole(MovableSprite):
    """Class representing VortexHole which can attract other items to it"""

    def __init__(self, x, y, radius = VORTEX_HOLE_RADIUS):
        self.radius = radius
        self.score = VORTEX_HOLE_SCORE
        self.hp = VORTEX_HOLE_HP
        self.color = VORTEX_HOLE_COLOR
        self.angle = 0

        diameter = self.radius*2
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)
        
        self.image = pygame.Surface([diameter, diameter])
        self.image.set_colorkey(BACKGROUND_COLOR)                
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        
        self.set_angle(self.angle)

        self.can_attract_objects = True
        self.attract_radius = VORTEX_HOLE_ATTRACT_RADIUS
        self.attract_acc = VORTEX_HOLE_ATTRACT_ACC
        self.attractable = False
        
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
    def hit(self):
        self.hp -= 1

        if self.hp <= 0:
            self.kill()
            
        return self.score

    def canAttractSprites(self):
        return self.can_attract_objects

    def attractSprite(self, sprite):
        # Start by checking if we can attract this object
        if(sprite is self):
            return None

        # Transparent objects can not be attracted
        if(sprite.transparent or not sprite.attractable):
            return None
        
        center_x = self.rect.centerx
        center_y = self.rect.centery

        b_side = sprite.x - center_x
        a_side = sprite.y - center_y
        
        distance = ((b_side**2) + (a_side**2))**0.5

        if(distance > self.attract_radius):
            return None

        if b_side == 0:
            attract_angle = 90
        else:
            attract_radians = math.atan(a_side/b_side)
            attract_angle = math.degrees(attract_radians)

        if b_side < 0:
            attract_angle = 180 + attract_angle

        if distance < 10:
            distance = 10

        g_acc = self.attract_acc / ((distance/10)**2)
        
        return (g_acc, attract_angle)
