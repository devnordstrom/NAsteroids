"""
Utillity class

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

SOUND_BASE_PATH = "src/data/sound/";

class SoundBox:
    """Class used for playing sound effects"""
    
    def __init__(self):
        self.sound_effects = []
        self.py_sounds = {}
        self.channel_number = 0
        
        self.load_sounds()
    
    def load_sounds(self):
        """Loads all the sound effects"""
        
        # Loads all the sounds in the base_directory.
        current_dir = os.getcwd()
        
        for sound_file in glob.glob(SOUND_BASE_PATH + "*.wav"):
            #sound_file = sound_file.replace(SOUND_BASE_PATH, '')
            self.sound_effects.append(sound_file)

        # Load the sound effects
        for effect in self.sound_effects:
            self.py_sounds[effect] = pygame.mixer.Sound(effect)
            
        os.chdir(current_dir)
        
    def play(self, sound_name):
        
        matching_sounds = []

        for sound_eff in self.sound_effects:
            if sound_name in sound_eff:
                matching_sounds.append(sound_eff)

        if len(matching_sounds) == 0:
            return
        
        choosen_effect = random.choice(matching_sounds)

        self.play_effect(choosen_effect)

    def play_effect(self, sound_effect):
        py_sound = self.py_sounds[sound_effect]

        pygame.mixer.Channel(self.channel_number).play(py_sound)
        self.channel_number = (self.channel_number+1) % 8
