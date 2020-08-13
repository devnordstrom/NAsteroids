"""
Utillity classes.

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
from constants import *
from functions import *

class SoundBox:
    """Class used for playing sound effects"""

    # This class should
    # 1) Load all sound effects available,
    # 2) Choose a random sound effect.
    # 3) Play the sound effect
    
    def __init__(self, base_dir = "sound/"):
        self.base_dir = base_dir
        self.sound_effects = []
        self.py_sounds = {}
        self.channel_number = 0
        
        self.load_sounds()
    
    def load_sounds(self):
        """Loads all the sound effects"""
        
        # Loads all the sounds in the base_directory.
        current_dir = os.getcwd()
        
        os.chdir(self.base_dir)
        
        for sound_file in glob.glob("*.wav"):
            self.sound_effects.append(sound_file)
        
        
        # Load the sound effects
        for effect in self.sound_effects:
            self.py_sounds[effect] = pygame.mixer.Sound(effect)
            
        os.chdir(current_dir)
        
    def play(self, sound_name):
        
        matching_sounds = []

        for sound_eff in self.sound_effects:
            if sound_eff.startswith(sound_name):
                matching_sounds.append(sound_eff)

        if len(matching_sounds) == 0:
            return
        
        choosen_effect = random.choice(matching_sounds)

        self.play_effect(choosen_effect)

    def play_effect(self, sound_effect):
        py_sound = self.py_sounds[sound_effect]

        pygame.mixer.Channel(self.channel_number).play(py_sound)
        self.channel_number = (self.channel_number+1) % 8
        
    

class TextMessage:
    """Class representing a text message to be displayed on the screen"""

    def __init__(self, message, x, y):
        self.message = message
        self.color = TEXT_COLOR
        self.spawn_time = get_millis()
        self.x = x
        self.y = y
        
    def is_active(self):
        return self.spawn_time > (get_millis() - TEXT_DISPLAY_TIME_MS)
