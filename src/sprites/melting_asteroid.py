import pygame
from .. import constants
from .movable_sprite import MovableSprite

MELTING_ASTEROID_HP = 5
MELTING_ASTEROID_SCORE = 20
MELTING_ASTEROID_MELT_FACTOR = 1

class MeltingAsteroid(MovableSprite):

    """This reprents an asteroid that will melt or shrink instead of shattering into smaller pieces"""
    def __init__(self, x, y, radius, sprite_image = "melting_asteroid.png"):
    
        #self.image = pygame.image.load(sprite_image).convert()

        diameter = radius * 2;
        self.radius = radius

        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        self.image = self.org_image
        self.image = pygame.transform.scale(self.image, (diameter, diameter))
        self.image.set_colorkey(constants.BACKGROUND_COLOR)

        self.redrawImage()

        MovableSprite.__init__(self, self.rect, self.image)
            
        self.hp = MELTING_ASTEROID_HP
        self.score = MELTING_ASTEROID_SCORE
        self.melt_factor = MELTING_ASTEROID_MELT_FACTOR

    def hit(self):
        self.hp -= 1
        
        if self.hp <= 0:
            self.kill()
        else:
            self.radius -= (self.melt_factor)
            self.redrawImage()
            
        return self.score

    def redrawImage(self):
        diameter = self.radius * 2
        oldCenterX, oldCenterY = self.rect.center

        # We must recreate the rectangle/surface object as this asteroid might have melted
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (oldCenterX, oldCenterY)
        
        self.image = pygame.transform.scale(self.image, (diameter, diameter))
        self.image.set_colorkey(constants.BACKGROUND_COLOR)

        self.mask = pygame.mask.from_surface(self.image)
