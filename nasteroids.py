"""
Asteroids inspired game made with Pygame

"""

# To do add more documentation


# Imports
import sys
import time
import random
import math
import pygame
import pygame.sprite
import pygame.mixer
import os
import glob
from pygame.locals import *
from constants import *
from sprites import *
from functions import *
from level import *
from util_classes import *

class Game:
    """Main class representing the Game"""
    
    def __init__(self):
        
        # Inits settings        
        self.init_gui()

        # Inits attributes.
        self.font = pygame.font.SysFont(None, GAME_INFO_FONT_SIZE)
        self.big_font = pygame.font.SysFont(None, GAME_INFO_BIG_FONT_SIZE)
        self.mainClock = pygame.time.Clock()
        
        self.sprite_group = pygame.sprite.Group()
        self.ship_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.sound_box = SoundBox()
        self.text_message = None
        self.level = None
        self.level_number = 0

        # Sets the starting level which will be incremented as the first
        # level is set thus why decrementing it here with one.
        if STARTING_LEVEL > 0:
            self.level_number = STARTING_LEVEL - 1
        
        self.level_count = 100
        self.respawn_player(False)
        self.lives = 0
        self.score = 0
            

    def init_gui(self):
        # The extra pygame.mixer code is added in order to
        # make the sound effects play instantly.
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        # Inits pygame.
        pygame.init()
        
        self.windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption(CAPTION)
        pygame.mouse.set_visible(False)

    def is_level_cleared(self):
        """Evaluates if the level is cleared and the next level should be set."""
        # Perhaps this should be moved to the level Class?
        if self.level is None or not self.level.has_spawn_delay_elapsed():
            return False

        if self.level.has_sprites:
            return False
            
        for sprite in self.sprite_group:
            if sprite.temporary or sprite.transparent:
                continue

            if isinstance(sprite, SpaceShip) or isinstance(sprite, Bullet):
                continue

            return False
            
        return True

    def has_next_level(self):
        return self.level_number < self.level_count

    def should_generate_next_level(self):
        if self.level is not None and not self.is_level_cleared():
            return False

        return self.has_next_level()
    
    def set_next_level(self):
        self.level_number += 1
        self.level = Level(self.level_number, self.player)
        self.set_message(f"Level: {self.level_number}")

    def set_message(self, message):
        x = (WINDOWWIDTH // 2) - 100
        y = WINDOWHEIGHT // 2
        
        self.text_message = TextMessage(message, x, y)        
        
        
    def hit_sprite(self, sprite):      
        score = sprite.hit()

        if score is not None:
            self.score += score
        
        if isinstance(sprite, Asteroid):
            self.sound_box.play("asteroid_split")
        elif isinstance(sprite, SlimeBlob):
            self.sound_box.play("slime_kill")
        elif isinstance(sprite, SpaceShip):
            self.sound_box.play("ship_kill")
        
        
        if sprite.should_split:
            split_sprites = sprite.split()
                                                    
            for split_sprite in split_sprites:
                self.add_sprite(split_sprite)
    
    def respawn_player(self, decrease_lives = True):
        if decrease_lives:
            self.lives -= 1
            
        self.player = SpaceShip(PLAYER_START_X, PLAYER_START_Y, PLAYER_DIAMETER)
        self.add_sprite(self.player)
        self.ship_group.add(self.player)
        
        self.sound_box.play("ship_respawn")

    def spawn_asteroid(self):
        ast_x, ast_y = 500, 500
        asteroid = Asteroid(ast_x, ast_y)
        asteroid.set_angle(random.randint(0, 360))
        asteroid.velocity = random.randint(50, 200) / 100

        self.add_sprite(asteroid)


    def fire_bullet(self):
        self.sound_box.play("laser_shoot")
        
        bullet = self.player.fire_bullet()
        self.sprite_group.add(bullet)
        self.bullet_group.add(bullet)
    
    def add_sprite(self, sprite):
        self.sprite_group.add(sprite)

    def draw_text(self, text, x, y, big_font = False):
        if big_font:
            font = self.big_font
        else:
            font = self.font
        
        textobj = font.render(text, 1, TEXT_COLOR)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.windowSurface.blit(textobj, textrect)

    def draw_info(self):
        info_x = GAME_INFO_BASE_X
        info_y = GAME_INFO_BASE_Y
        info_margin = GAME_INFO_MARGINS
        
        # Draws level number
        level_nr = ""
        if self.level_number > 0:
            level_nr = self.level_number
        self.draw_text(f"Level: {level_nr}", info_x, info_y)
         
        # Draws number of lives. self.lives
        info_y += info_margin
        self.draw_text(f"Lives: {self.lives}", info_x, info_y)

        # Draws player score
        info_y += info_margin
        self.draw_text(f"Score: {self.score}", info_x, info_y)

        if self.text_message is not None and self.text_message.is_active():
            message = self.text_message.message
            x, y = self.text_message.x, self.text_message.y
            self.draw_text(message, x, y, True)
        

    def draw_background(self):
        self.windowSurface.fill(BACKGROUND_COLOR)

    def draw_sprites(self):
        for sprite in self.sprite_group:
            sprite.draw(self.windowSurface)
        
    def start_campaign(self):
        print("start_campaign() called")
        
        self.start_game_loop()
    
    def should_respawn_player(self):
        if self.lives <= 0:
            return False
        
        player_time_dead_ms = get_millis() - self.player.kill_time_ms
        return player_time_dead_ms > PLAYER_RESPAWN_TIME_MS
    
    def start_game_loop(self):

        self.game_running = True
        self.lives = PLAYER_STARTING_LIVES        

        #starts game loop.
        while self.game_running:
            # Manages if the player should respawn.
            if not self.player.alive():
                if self.should_respawn_player():
                    self.respawn_player()
                    
                    
            # Handles events
            for event in pygame.event.get():
                self.manage_event(event)
            
            # Moves sprites
            for mov_sprite in self.sprite_group:
                self.move_sprite(mov_sprite)

                                     
            # Draws text and background color.
            self.draw_background()
            
            self.draw_info()

            
            # Draws sprites
            self.draw_sprites()

            # Manages sounds and sound effects.
            self.manage_sounds()

            # Manages collision detection
            for sprite in self.sprite_group:
                self.check_collision(sprite)


            # Adds sprites if the level has any that should be added.
            if self.level is not None and self.level.has_sprites:
                for lvl_spr in self.level.get_sprites():
                    self.add_sprite(lvl_spr)

            # Manages level logic
            if self.should_generate_next_level():
                self.set_next_level()                            
            
            # Updates the display        
            pygame.display.update()
            self.mainClock.tick(FPS)

    def manage_sounds(self):
        """Manages sounds"""
        if self.player.alive() and self.player.thrust_on:
            self.sound_box.play("ship_thrust")
            
            
            
    def move_sprite(self, mov_sprite):

        # Checks if the target should be set.
        if isinstance(mov_sprite, SlimeBlob):
            mov_sprite.set_target(self.player.rect.centerx, self.player.rect.centery)
            
        # This moves and rotates the MovableSprite.
        mov_sprite.update()

        # No need to do anything else if the sprite is inside the screen.
        if WINDOW_SCREEN.colliderect(mov_sprite):
            return
                    
        # Removes temporary items that are
        # supposed to dissapeaer when off screen.
        if mov_sprite.temporary:
            mov_sprite.kill()
            return

        # Now moving the sprite from one side of the screen
        # To the opposite.
        new_x = mov_sprite.x
        new_y = mov_sprite.y
                    
        # Checks/Corrects if it goes outside to the left or right.
        if mov_sprite.rect.right < 0:
            new_x = WINDOW_SCREEN.width + (mov_sprite.rect.height//2)
        elif mov_sprite.rect.left > WINDOW_SCREEN.width:
            new_x = 0 - (mov_sprite.rect.width//2)

        # Checks/Corrects if it goes outside to the top or bottom.
        if mov_sprite.rect.bottom < 0:
            new_y = WINDOW_SCREEN.height + (mov_sprite.rect.height//2)
        elif mov_sprite.rect.top > WINDOW_SCREEN.height:
            new_y = 0 - (mov_sprite.rect.height//2)

        # Sets x/y coordinate using this function
        # so that floating point values can be saved nicely.
        mov_sprite.set_pos(new_x, new_y)


    def check_collision(self, sprite):
        if isinstance(sprite, SpaceShip):
            self.check_ship_collision(sprite)
        elif isinstance(sprite, Bullet):
            self.check_bullet_collision(sprite)

                    
    def check_ship_collision(self, ship):        
        if ship.transparent:
            return
                
        colliding_sprites = self.get_colliding_sprites(ship)

        for col_sprite in colliding_sprites:
            # Ignores bullets for now.
            if col_sprite in self.bullet_group or col_sprite.transparent:
                continue

            # A ship may only hit one object per frame.
            ship.hit()
                    
            self.hit_sprite(col_sprite)
            break


    def check_bullet_collision(self, bullet):
        colliding_sprites = self.get_colliding_sprites(bullet)

        for sprite in colliding_sprites:
            # A bullet can't hit the object that shot it.
            if bullet.parent is sprite or isinstance(sprite, Bullet) or isinstance(sprite, SpaceShip):
                continue
            
            bullet.kill()

            self.hit_sprite(sprite)
            break
    
    def get_colliding_sprites(self, sprite):
        # This is too long.
        return pygame.sprite.spritecollide(sprite, self.sprite_group, False, collision_detect)
                    
    def manage_event(self, event):
        if event.type == QUIT:
            terminate()
                
        if not self.player.alive():
            return
                                
        # Handles key pressed.
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.player.set_thrust_on(True)
            elif event.key == K_DOWN:
                self.player.set_break(True)    
            if event.key == K_RIGHT:
                self.player.rotate_clockwise(True)
            if event.key == K_LEFT:
                self.player.rotate_counter_clockwise(True)
            if event.key == K_SPACE:
                self.fire_bullet()
                        
        if event.type == KEYUP:
            if event.key == K_UP:
                self.player.set_thrust_on(False)
            if event.key == K_DOWN:
                self.player.set_break(False)
            if event.key == K_RIGHT:
                self.player.rotate_clockwise(False)
            if event.key == K_LEFT:
                self.player.rotate_counter_clockwise(False)

    
    

def main():
    """main method used for starting the program."""

    # Loads the Game class and starts the campaign.
    game = Game()
    game.start_campaign()
    
    
# Starts the program
if __name__ == '__main__':
    main()
