"""Class containing objects or sprites such as asteroids and shipes."""

# Imports
import sys
import time
import random
import math
import pygame
import pygame.sprite
import pygame.mixer
from pygame.locals import *
from constants import *
from functions import *

# To do move classes to seperate files.
# Also add documentation

# Class definitions.
class MovableSprite(pygame.sprite.Sprite):
    """Base class for the sprites or objects in the game."""
    
    def __init__(self, rect, image):
        # Calls parent constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.rect = rect

        # Using an additional image field "org_image"
        # so a transformed or rotated copy can be used.
        if not hasattr(self, 'org_image'):
            self.org_image = image
        
        self.image = image

        # Sets the default attributes unless they are allready set.
        if not hasattr(self, 'velocity'):
            self.velocity = 0
        if not hasattr(self, 'acc'):
            self.acc = 0
        if not hasattr(self, 'angle'):
            self.angle = 0
        if not hasattr(self, 'mov_angle'):
            self.mov_angle = 0
        if not hasattr(self, 'should_split'):
            self.should_split = False
        if not hasattr(self, 'temporary'):
            self.temporary = False
        if not hasattr(self, 'transparent'):
            self.transparent = False
        if not hasattr(self, 'max_velocity'):
            self.max_velocity = -1
        if not hasattr(self, 'x'):
            self.x = rect.centerx
        if not hasattr(self, 'y'):
            self.y = rect.centery

        # Sets the collision mask.
        self.update_mask()
        
        
    def set_angle(self, angle, set_mov_angle = True):
        """This class sets the angle and if desired movement angle,
            this will also updates the mask."""
        
        # No need to do anything else if the angle hasn't been changed.
        if hasattr(self, "angle") and self.angle == angle:
            return
        
        self.angle = angle

        # Sometimes the movement angle shouldn't be changed,
        # this might be when the players ship wants to rotate
        # without the ship currently accelerating.
        if set_mov_angle:
            self.mov_angle = angle
        
        # Using -self.angle since rotate is counter clock wise.
        self.image = pygame.transform.rotate(self.org_image, -self.angle)

        # Recreates the bounding rect with the same
        # center as before to accomodate the rotated image.
        old_center = self.rect.center
        
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        self.set_pos(self.x, self.y)

        # Updates the mask used for collission detection.
        self.update_mask()
    
    def set_pos(self, x, y):
        # Weird, hard to see if the x and y are the topleft corner or the center coords.
        self.x = x
        self.y = y

        self.rect.centerx = round(x)
        self.rect.centery = round(y)

    def update(self):
        """sprites"""
        self.rotate()
        
        self.move()

    def update_mask(self):
        """Updates the mask used for pixel perfect collision detection."""
        self.mask = pygame.mask.from_surface(self.image)

    def hit(self):
        pass
    
    def rotate(self):
        """Support for rotating classes in subclasses possible."""
        pass

    def move_deacc(self):
        """ This function deaccelerates the body,
            but will not change the movement angle."""
        
        # Deaccelerates velocity based on the acceleration of the object.                
        self.velocity -= abs(self.acc)

        # The body/object isn't allowed to go backwards.
        if self.velocity < 0:
            self.velocity = 0
        
        mov_angle = self.mov_angle
        mov_radians = math.radians(self.mov_angle)

        x_speed = self.velocity * math.cos(mov_radians)
        y_speed = self.velocity * math.sin(mov_radians)

        x_pos = self.x+x_speed
        y_pos = self.y+y_speed

        self.set_pos(x_pos, y_pos)
        

    def move(self):
        """Moves the object, taking into account current angle
           and previous angle/velocity and acceleration"""

        # Using different method if the acceleration is supposed to be negative.
        if self.acc < 0:
            self.move_deacc()
            return
        
        # Figuring out what acceleration to add based on the angle the object is facing
        # Converting to radians since that is what the math library supports.
        radians = math.radians(self.angle)
        x_acc = self.acc * math.cos(radians)
        y_acc = self.acc * math.sin(radians)
        
        
        # Calculates the old x/y speed.
        old_mov_radians = math.radians(self.mov_angle)
        old_x_speed = self.velocity * math.cos(old_mov_radians)
        old_y_speed = self.velocity * math.sin(old_mov_radians)
                
        # Changes x/y dir and movement angle based on
        # acceleration and angle objects facing.
        x_speed = old_x_speed + x_acc
        y_speed = old_y_speed + y_acc
        self.velocity = ((x_speed**2)+(y_speed**2))**0.5

        
        if self.velocity != 0:
            # We know the x_speed, y_speed, velocity, now setting angle.
            mov_radians = math.asin(y_speed / self.velocity)
            self.mov_angle = math.degrees(mov_radians)

            # Flips the angle in case the x_speed is negative.
            if x_speed < 0:
                old_mov_angle = self.mov_angle
                self.mov_angle = 180 - self.mov_angle
                mov_radians = math.radians(self.mov_angle)
        
        # If the max velocity is set and the velocity
        # exceeds max velocity then nerf it and change x/y dir.
        if self.max_velocity > 0 and self.velocity > self.max_velocity:
            self.velocity = self.max_velocity
            x_speed = math.cos(mov_radians) * self.velocity
            y_speed = math.sin(mov_radians) * self.velocity
        
            
        
        # Sets the new x and y position.
        x = self.x
        y = self.y
        
        x_pos = x+x_speed
        y_pos = y+y_speed

        
        # This has been verified, seems all good thus far.
        
        # Adds x/y velocity to x/y coordinates
        self.set_pos(x_pos, y_pos)
    
    def draw(self, surface):
        """Draws the image."""
        surface.blit(self.image, self.rect)
        

class Meteorite(MovableSprite):
    """Class representing a meteroite which may collide with the player."""
    
    def __init__(self, x, y, radius):
        diameter = radius*2
        self.radius = radius
        self.color = METEROITE_COLOR
        
        
        self.rect = Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        self.image = pygame.Surface([diameter, diameter])
        self.image.set_colorkey(BACKGROUND_COLOR)                
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        
        # Calls parent constructor
        MovableSprite.__init__(self, self.rect, self.image)
        
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 1
        self.score = METEROITE_SCORE

    def hit(self):
        self.hp -= 1

        if self.hp <= 0:
            self.kill()
            
        return self.score
    
    def shatter(self):
        return []


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
            sub_objects.append(self.split_asteroid(sub_objects))
        
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

class ClusterAsteroid(Asteroid):
    """Class representing Asteroids that can
        shatter into smaller asteroids on being hit"""

    def __init__(self, x, y, radius = ASTEROID_RADIUS, sprite_image = "sprites/asteroid_cluster.png"):

        cluster_radius = ASTEROID_RADIUS * 2
        
        Asteroid.__init__(self, x, y, cluster_radius, sprite_image)
        
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


class Bullet(MovableSprite):
    """Class representing bullet fired."""
    
    def __init__(self, left, top, radius = BULLET_RADIUS, bullet_color = BULLET_COLOR):
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
        
    

class SpaceShip(MovableSprite):
    """Class representing a spaceship, should perhaps inherit from MovableSprite."""
    
    def __init__(self, left, top, diameter):
        self.color = PLAYER_COLOR
        self.rect = Rect(left, top, diameter, diameter)

        # Creates the image
        self.org_image = pygame.Surface([diameter, diameter])
        self.org_image.set_colorkey(BACKGROUND_COLOR)
        
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
        bullet_x = self.rect.centerx - BULLET_RADIUS
        bullet_y = self.rect.centery - BULLET_RADIUS
        
        bullet = Bullet(bullet_x, bullet_y)
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
