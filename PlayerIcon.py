import pygame as pg
from pygame.locals import *
import math


class PlayerIcon:
    def __init__(self, themeManager, game, position, size: tuple, playerId: int):
        self.game = game
        self.size = size
        self.themeManager = themeManager
        self.originalPosition = position
        self.position = position
        self.playerId = playerId


    def image(self):
        image = self.themeManager.getPlayerIcon(self.playerId, self.game.mode)
        return pg.transform.smoothscale(image, self.size)


    def draw(self, surface: pg.Surface):
        if self.game.activePlayer == self.playerId:
            self.animate(surface)
            surface.blit(self.image(), self.position)
        else: 
            surface.blit(self.image(), self.originalPosition)


    def animate(self, surface: pg.Surface):
        self.position = (self.originalPosition[0], self.originalPosition[1] + 15 * math.sin(pg.time.get_ticks() / 200))