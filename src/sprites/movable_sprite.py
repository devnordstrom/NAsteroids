# Imports
import math
import pygame
import pygame.sprite
from ..functions import add_vectors

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
        if not hasattr(self, 'remove_off_scren'):
            self.remove_off_scren = False
        if not hasattr(self, 'friendly'):
            self.friendly = False
        if not hasattr(self, 'toxic'):
            self.toxic = False
        if not hasattr(self, 'attractable'):
            self.attractable = True
        if not hasattr(self, 'max_velocity'):
            self.max_velocity = -1
        if not hasattr(self, 'x'):
            self.x = rect.centerx
        if not hasattr(self, 'y'):
            self.y = rect.centery
        if not hasattr(self, 'a_acc_angle'):
            self.a_acc_angle = 0
        if not hasattr(self, 'a_acc'):
            self.a_acc = 0
        
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

    def add_acc(self, a_acc, a_angle):
        """Add acceleration with the specified angle."""

        newVector = add_vectors(self.a_acc, self.a_acc_angle, a_acc, a_angle)

        #print("add_acc newVector: (" + str(newVector[0]) + ", "+ str(newVector[1]) +")")
        
        self.a_acc = newVector[0]
        self.a_acc_angle = newVector[1]
        
    def set_pos(self, x, y):
        # TODO this function is weird...
        self.x = x
        self.y = y

        self.rect.centerx = round(x)
        self.rect.centery = round(y)

    def update(self):
        """sprites"""
        self.rotate()
        
        self.move()

        self.a_acc = 0
        self.a_acc_angle = 0        

    def update_mask(self):
        """Updates the mask used for pixel perfect collision detection."""
        self.mask = pygame.mask.from_surface(self.image)

    def hit(self):
        return 0
    
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

        # Using different method if we're slowing down
        if self.acc < 0:
            self.move_deacc()
            return

        avector = add_vectors(self.acc, self.angle, self.a_acc, self.a_acc_angle)
        acc = avector[0]
        angle = avector[1]
        
        # Figuring out what acceleration to add based on the angle the object is facing
        # Converting to radians since that is what the math library supports.
        radians = math.radians(angle)
        x_acc = acc * math.cos(radians)
        y_acc = acc * math.sin(radians)
        
        
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
        
        # Adds x/y velocity to x/y coordinates
        self.set_pos(x_pos, y_pos)
    
    def draw(self, surface):
        """Draws the image."""
        surface.blit(self.image, self.rect)

    def canAttractSprites(self):
        return False

    def attractSprite(self, sprite):
        """Function allowing the sprite to attract or repel other sprites, most implementations won't use this"""
        pass
