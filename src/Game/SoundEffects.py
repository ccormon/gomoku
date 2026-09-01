import pygame as pg
from pygame.locals import *


class SoundEffects:
    def __init__(self):
        self.active = True
        self.sounds = {
            "pop": pg.mixer.Sound("assets/sound/pop_sound.mp3"),
            "piece": pg.mixer.Sound("assets/sound/piece_sound.mp3"),
        }


    def play_sound(self, name: str):
        if name in self.sounds and self.active:
            self.sounds[name].play()


    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(volume)


    def toggle(self):
        self.active = not self.active
