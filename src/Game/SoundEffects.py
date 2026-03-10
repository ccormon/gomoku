import pygame as pg
from pygame.locals import *


class SoundEffects:
    def __init__(self):
        self.active = True
        self.sounds = {
            "pop": pg.mixer.Sound("assets/sound/pop_sound.mp3")}


    def play_sound(self, name: str):
        if name in self.sounds and self.active:
            self.sounds[name].play()


    def toggle(self):
        self.active = not self.active