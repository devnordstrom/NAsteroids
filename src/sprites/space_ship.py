import pygame
from ..constants import *
from ..functions import *
from .movable_sprite import MovableSprite
from .bullet import Bullet

# Constants
PLAYER_ROTATE_SPEED = 5
PLAYER_ACC = 0.15
PLAYER_BREAK_DEACC = -0.25
PLAYER_MAX_SPEED = 10
PLAYER_COLOR = (153, 0, 0, 0.7)
PLAYERWIDTH = 50

PLAYER_SPAWN_SAFE_TIME_MS = 3 * 1000

ROTATE_CLOCKWISE = 1
ROTATE_NONE = 0
ROTATE_COUNTER_CLOCKWISE = -1

class SpaceShip(MovableSprite):
    """Class representing a spaceship, should perhaps inherit from MovableSprite."""
    
    def __init__(self, left, top, diameter):
        self.color = PLAYER_COLOR
        self.rect = Rect(left, top, diameter, diameter)

        # Creates the image
        self.org_image = pygame.Surface([diameter, diameter])
        self.org_image.set_colorkey(BACKGROUND_COLOR)

        # For now this spaceship is just a triangle but looks cool nonetheless
        pygame.draw.polygon(self.org_image, self.color, ((0, 0), (diameter, diameter/2), (0, diameter)))        
        self.image = self.org_image.copy()

        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
        self.rotate_speed = PLAYER_ROTATE_SPEED
        self.rotate_dir = ROTATE_NONE
        self.set_angle(0)
        self.acc = 0
        self.thrust_acc = PLAYER_ACC
        self.break_deacc = PLAYER_BREAK_DEACC
        self.max_velocity = PLAYER_MAX_SPEED
        self.velocity = 0
        self.speed = 0
        self.acc = 0
        self.score = 0
        self.hp = 1
        self.temporary = False
        self.friendly = True
        self.thrust_on = False
        self.bullets = []
        self.kill_time_ms = 0
        self.spawn_time_ms = get_millis()
        
        # Transparent/Invulnarable when spawning
        self.transparent = True
        self.update_mask()
        
    def kill(self):
        if not self.alive():
            return
        
        self.kill_time_ms = get_millis()
        MovableSprite.kill(self)

    def set_thrust_on(self, thrust_on):
        self.thrust_on = thrust_on

        if thrust_on:
            self.acc = self.thrust_acc
        else:
            self.acc = 0
        
    
    def set_acc_forward(self, acc_forward):
        if acc_forward:
            self.acc = self.thrust_acc
        else:
            self.acc = 0
            
    def set_break(self, should_break):
        if should_break:
            self.acc = self.break_deacc
        else:
            self.acc = 0

    def rotate_clockwise(self, rotate):
        if rotate:
            self.rotate_dir = ROTATE_CLOCKWISE
        else:
            self.rotate_dir = ROTATE_NONE

    def rotate_counter_clockwise(self, rotate):
        if rotate:
            self.rotate_dir = ROTATE_COUNTER_CLOCKWISE
        else:
            self.rotate_dir = ROTATE_NONE

    def update(self):        
        # Rotates the ship
        self.rotate()
        
        # Moves the ship
        self.move()
        
        # Toggles transparency if the ship respawned
        if self.transparent and (get_millis() - self.spawn_time_ms)> PLAYER_SPAWN_SAFE_TIME_MS:
            self.transparent = False

        self.a_acc = 0
        self.a_acc_angle = 0
        
    def rotate(self):
        """Rotates the spaceship."""
        if self.rotate_dir == ROTATE_NONE:
            return

        new_angle = self.angle
        
        if self.rotate_dir == ROTATE_CLOCKWISE:
            new_angle += self.rotate_speed
        elif self.rotate_dir == ROTATE_COUNTER_CLOCKWISE:
            new_angle -= self.rotate_speed

        new_angle %= 360

        self.set_angle(new_angle, False)       
        
    def fire_bullet(self):        
        bullet = Bullet()

        bullet_x = self.rect.centerx - bullet.radius
        bullet_y = self.rect.centery - bullet.radius
        
        bullet.set_pos(bullet_x, bullet_y)
        bullet.parent = self
        bullet.fire(self.angle)
        return bullet
    
    def draw(self, surface):
        # Blinks the ship if it's transparent.
        if self.transparent and (get_millis() % 200) < 100:
            return

        surface.blit(self.image, self.rect)
        
        
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
        return self.score
