"""
This class controls the game including moving sprites, checking for collisions, checking if the level is complete e.t.c

TODO Possibly split this up into several classes

"""

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
from .constants import *

from .sprites.asteroid import Asteroid
from .sprites.slime_blob import SlimeBlob
from .sprites.space_ship import SpaceShip
from .sprites.bullet import Bullet

#from .sprites import asteroid.Asteroid as Asteroid
#from .sprites import slime_blob.SlimeBlob as SlimeBlob
#from .sprites import space_ship.SpaceShip as SpaceShip
#from .sprites import bullet.Bullet as Bullet

#from .sprites import * #asteroid.Asteroid as Asteroid, slime_blob.SlimeBlob as SlimeBlob, space_ship.SpaceShip as SpaceShip, bullet.Bullet as Bullet
from .functions import *

from .level.level import Level
from .level.campaign_level import CampaignLevel

from .level import *
from .text_message import *
from .sound_box import *

# constants
GAME_INFO_FONT_SIZE = 30
GAME_INFO_BIG_FONT_SIZE = 60
GAME_INFO_MARGINS = 20
GAME_INFO_BASE_X = GAME_INFO_MARGINS
GAME_INFO_BASE_Y = GAME_INFO_MARGINS

class Game:
    """Main class representing the Game"""
    
    def __init__(self, surface):
        
        # Inits attributes.
        self.windowSurface = surface
        self.font = pygame.font.SysFont(None, GAME_INFO_FONT_SIZE)
        self.big_font = pygame.font.SysFont(None, GAME_INFO_BIG_FONT_SIZE)
        self.mainClock = pygame.time.Clock()
        
        self.sprite_group = pygame.sprite.Group()
        self.ship_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.gas_wall_group = pygame.sprite.Group()
        self.sound_box = SoundBox()
        self.text_message = None
        self.level = None
        self.level_number = 0

        # Sets the starting level which will be incremented as the first
        # level is set thus why decrementing it here with one.
        if STARTING_LEVEL > 0:
            self.level_number = STARTING_LEVEL
        
        self.level_count = 100
        self.respawn_player(False)
        self.lives = 0
        self.score = 0
        self.has_gas_walls = False
    
    def is_level_cleared(self):
        """Evaluates if the level is cleared and the next level should be set."""
        if self.level is None:
            return False

        return self.level.is_cleared(self.sprite_group)

    def has_next_level(self):
        return self.level_number < self.level_count

    def should_generate_next_level(self):
        if self.level is not None and not self.is_level_cleared():
            return False

        return self.has_next_level()
    
    def generate_next_level(self):
        self.level_number += 1
        level = CampaignLevel(self.level_number, WINDOWWIDTH, WINDOWHEIGHT)
        self.set_level(level)
        
    def set_level(self, level):
        self.level = level
        self.set_message( level.name )
        self.toggle_gas_walls(self.level.has_letal_walls())

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
        
        # TODO What if we want to enable a sprite to "split" or spawn other sprites after a certain time automatically?
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

    def spawn_vortex_hole(self):
        """Spawns a new vortex hole"""

        vx = random.randint(200, WINDOWWIDTH-200)
        vy = random.randint(100, WINDOWHEIGHT-100)
        
        vortex_hole = VortexHole(vx, vy)
        self.add_sprite(vortex_hole)

    def spawn_melting_asteroid(self):
        print("Now spawning a melting asteroid")
        
        ast_x, ast_y = 500, 500
        masteroid = MeltingAsteroid(ast_x, ast_y, 70, "sprites/melting_asteroid_a.png")
        masteroid.set_angle(random.randint(0, 360))
        masteroid.velocity = random.randint(50,70) / 100

        self.add_sprite(masteroid)

    def activate_nuke(self):
        """"""

        print("activate_nuke started!")
        
        hit_count = 0

        for sprite in self.sprite_group:

            if isinstance(sprite, Bullet) or isinstance(sprite, SpaceShip):
                continue
            
            self.hit_sprite(sprite)
            hit_count += 1
        
        print("activate_nuke hit_count = "+str(hit_count))
    
    def add_sprite(self, sprite):
        self.sprite_group.add(sprite)

    def toggle_gas_walls(self, use_gas_walls):
        if use_gas_walls == self.has_gas_walls:
            return

        if use_gas_walls:
            
            width, height = self.windowSurface.get_size()
            wall_width = 10

            print("toggle_gas_walls width: "+ str( width ) +", height: " + str( height))
            
            #leftWall = GassWall(0, 0, wall_width, height)
            #topWall = GassWall(wall_width, 0, width-wall_width, wall_width)
            rightWall = GassWall(width-wall_width, wall_width, width, height)
            bottomWall = GassWall(wall_width, height-wall_width, width, wall_width)

            self.gas_wall_group.add(leftWall)
            self.gas_wall_group.add(topWall)
            self.gas_wall_group.add(rightWall)
            self.gas_wall_group.add(bottomWall)
        else:
            for wall in self.gas_wall_group:
                wall.kill()
            
        self.has_gas_walls = use_gas_walls

    # TODO Move function to MainGui class possibly?
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

        # This ensures the gas walls are drawn last
        if self.has_gas_walls:
            self.draw_gas_walls()

            
    def draw_gas_walls(self):
        for wall in self.gas_wall_group:
            wall.draw(self.windowSurface)
            
        
    def start(self):
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
            if self.level is not None and self.level.has_sprites():
                for lvl_spr in self.level.get_sprites():
                    self.add_sprite(lvl_spr)

            # Manages level logic
            if self.should_generate_next_level():
                self.generate_next_level()                            
            
            # Updates the display        
            pygame.display.update()
            self.mainClock.tick(FPS)

    def manage_sounds(self):
        """Manages sounds"""

        # TODO Refactor this, seems as if there should be a better way to do this
        if self.player.alive() and self.player.thrust_on:
            self.sound_box.play("ship_thrust")
            
    def move_sprite(self, mov_sprite):

        # Checks if the target should be set.
        # TODO replace by adding a property "targets_player" insetad of checking the type
        if isinstance(mov_sprite, SlimeBlob) and self.player.alive and not self.player.transparent:
            mov_sprite.set_target(self.player.rect.centerx, self.player.rect.centery)

        # Manages sprites that can attract/repel other sprites
        if mov_sprite.canAttractSprites():
            for sprite in self.sprite_group:
                
                attractVector = mov_sprite.attractSprite(sprite)

                if attractVector is not None:
                    attract_acc = attractVector[0]
                    attract_angle = attractVector[1]
                    
                    sprite.add_acc(attract_acc, attract_angle)
                
                
        # This moves and rotates the MovableSprite.
        # TODO Shouldn't the sprite move before attracting/repelling other obejcts?
        mov_sprite.update()

        # No need to do anything else if the sprite is inside the screen.
        if WINDOW_SCREEN.colliderect(mov_sprite):
            return

        # If gas walls are enabled we kill the players ship if they are outside the screen
        if self.has_gas_walls and isinstance(mov_sprite, SpaceShip):
            mov_sprite.kill()
            
        # Removes sprites sprites that are
        # supposed to dissapear when off screen.
        if mov_sprite.remove_off_scren:
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
            # Ignores bullets fired by the ship and transparent sprites unless they are toxic
            if col_sprite in self.bullet_group or (col_sprite.transparent and not col_sprite.toxic):
                continue

            # A ship may only be hit by one object per frame even if it simultaneoulsly crashes into several objects.
            ship.hit()
                    
            self.hit_sprite(col_sprite)
            break


    def check_bullet_collision(self, bullet):
        colliding_sprites = self.get_colliding_sprites(bullet)

        for sprite in colliding_sprites:
            # A bullet can't hit the object that shot it.
            if sprite.transparent or bullet.parent is sprite or isinstance(sprite, Bullet) or isinstance(sprite, SpaceShip):
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
            if event.key == K_n:
                self.activate_nuke()
            if event.key == K_b:
                self.spawn_vortex_hole()
            if event.key == K_q:
                self.spawn_melting_asteroid()
                
        if event.type == KEYUP:
            if event.key == K_UP:
                self.player.set_thrust_on(False)
            if event.key == K_DOWN:
                self.player.set_break(False)
            if event.key == K_RIGHT:
                self.player.rotate_clockwise(False)
            if event.key == K_LEFT:
                self.player.rotate_counter_clockwise(False)
