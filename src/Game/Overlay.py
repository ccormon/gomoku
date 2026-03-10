import pygame as pg
from pygame.locals import *

from src.Game.ThemeManager import ThemeManager

class Overlay:
    def __init__(self, size=(1600, 600), color=(255, 255, 255), alpha=160):
        self.size = size
        self.color = color
        self.alpha = alpha
        self.surface = pg.Surface(self.size)
        self.surface.set_alpha(self.alpha)
        self.surface.fill(self.color)


    def draw(self, display, game):
        # TODO: Refactor this to use ThemeManager for font and colors + make it look nicer
        font = pg.font.SysFont("Arial", 70)
        message = font.render(f"Victoire du Joueur {game.winner} !", True, (0, 0, 0))
        self.surface.blit(message, (self.size[0] // 2 - message.get_width() // 2, self.size[1] // 2 - message.get_height() // 2))
        font = pg.font.SysFont("Arial", 45)
        message = font.render(f"Temps moyen pour jouer :", True, (0, 0, 0))
        message2 = font.render(f"Joueur 1: {round(game.timerHistory[0][1], 2)}s", True, (0, 0, 0))
        message3 = font.render(f"Joueur 2: {round(game.timerHistory[1][1], 2)}s", True, (0, 0, 0))
        self.surface.blit(message, (self.size[0] // 2 - message.get_width() // 2, self.size[1] // 2 + 40))
        self.surface.blit(message2, (self.size[0] // 2 - message2.get_width() // 2, self.size[1] // 2 + 70))
        self.surface.blit(message3, (self.size[0] // 2 - message3.get_width() // 2, self.size[1] // 2 + 100))
        display.blit(self.surface, (0, 150))