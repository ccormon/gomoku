import pygame as pg
from pygame.locals import *

from MusicPlayer import MusicPlayer
from Game import GameMode


class ThemeManager:
    def __init__(self, themes, window, default: str="classic"):
        self.themes = themes
        self.window = window
        self.current = None
        self._images = {}
        self.setTheme(default)


    def getPlayerIcon(self, playerId: int, gamemode: GameMode):
        if gamemode == GameMode.PVP:
            return self._images["icon_player1"] if playerId == 1 else self._images["icon_player2"]
        elif gamemode == GameMode.PVE:
            return self._images["icon_player1"] if playerId == 1 else self._images["icon_playerIA"]
        else:
            raise ValueError("Invalid game mode")


    def getPiecesImage(self, playerId: int):
        if playerId == 1:
            return self._images["stone_player1"]
        elif playerId == 2:
            return self._images["stone_player2"]
        else:
            raise ValueError("Invalid player ID")


    def getBackground(self):
        return self._images.get("background")


    def getBoardColor(self):
        return self.current["colors"]["grid"]


    def setTheme(self, name: str):
        self.current = self.themes[name]
        self.fontName = self.current["font"]
        self._loadImages()
        self._load_music()


    def _loadImages(self):
        self._images.clear()
        for key, path in self.current["images"].items():
            self._images[key] = pg.image.load(path).convert_alpha()


    def _load_music(self):
        musicPath = self.current.get("music")
        if musicPath:
            self.window.musicPlayer.load(musicPath)