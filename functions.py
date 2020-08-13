import sys
import time
import random
import pygame
import pygame.sprite
from pygame.locals import *
from constants import *

# Function definitions.
def terminate():
    print(f"Thanks so much for playing {GAME_NAME} and have a nice day!")
    pygame.quit()
    sys.exit()
    
def collision_detect(sprite_a, sprite_b):
    # Excludes the same sprite object since it will always collide with itself.
    if sprite_a is sprite_b:
        return False

    # Checks if the bounding rects collides first.
    # This improves performance as pixel perfect collision takes
    # much more computing power.
    if not sprite_a.rect.colliderect(sprite_b.rect):
        return False

    # Finally does pixel perfect collision with masks.
    return pygame.sprite.collide_mask(sprite_a, sprite_b)    

def get_millis():
        return time.time_ns() // 1000000

def generate_angle(occupied_angles = []):
    """Generates a random angle and also avoids duplicate
        angles based on the occupied angles supplied, albeit
        this won't work flawlessly if more than 2 angles are to be
        generated."""

    angle = random.randint(0, 360)

    for o_a in occupied_angles:
        if angle == o_a:
            angle += 20

    # Perfectly straight angles are banned in order
    # to prevent objects from endlessly drifting at
    # the edge of the screen such as an asteroid fragment
    # at the top of the screen drifting perfectly horizontally
    # and thus never being shown.
    if angle % 90 == 0:
        angle += random.choice([-1, 1])

    return angle

def load_image(image_path, loaded_images = {}):
    """Function intened for lazy loading and caching images."""

    # Checks if the image is cached and then returns it.
    if image_path in loaded_images:
        return loaded_images[image_path]

    # Loads the image
    loaded_image = pygame.image.load(image_path).convert()

    # Caches the image and then returns it.
    loaded_images[image_path] = loaded_image
    
    return loaded_image
