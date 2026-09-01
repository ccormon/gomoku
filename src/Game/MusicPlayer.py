import pygame as pg
from pygame.locals import *


class MusicPlayer:
    def __init__(self):
        self.musicFile = None
        self.enabled = True
        self.volume = 1.0


    def load(self, musicFile):
        if musicFile == self.musicFile:
            return
        self.musicFile = musicFile
        pg.mixer.music.load(musicFile)
        pg.mixer.music.set_volume(self.volume)
        pg.mixer.music.play(-1)
        if not self.enabled:
            pg.mixer.music.pause()


    def play(self, loops: int=-1):
        self.enabled = True
        pg.mixer.music.play(loops)


    def pause(self):
        self.enabled = False
        pg.mixer.music.pause()


    def unpause(self):
        self.enabled = True
        pg.mixer.music.unpause()


    def is_playing(self):
        return pg.mixer.music.get_busy()


    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        self.volume = volume
        pg.mixer.music.set_volume(self.volume)
