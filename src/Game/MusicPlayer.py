import pygame as pg
from pygame.locals import *


class MusicPlayer:
    def __init__(self):
        #pg.mixer.music.load(musicFile)
        pass


    def load(self, musicFile):
        pg.mixer.music.load(musicFile)


    def play(self, loops: int=-1):
        pg.mixer.music.play(loops)


    def pause(self):
        pg.mixer.music.pause()


    def unpause(self):
        pg.mixer.music.unpause()


    def is_playing(self):
        return pg.mixer.music.get_busy()


    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(volume)