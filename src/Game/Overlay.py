import pygame as pg
from pygame.locals import *

from src.Game.ThemeManager import ThemeManager
from src.Game.Position import Position


class _Canvas:
    # Size context so Position can compute overlay-relative coordinates
    def __init__(self, size: tuple):
        self.size = size


class Overlay:
    def __init__(self, themeManager: ThemeManager, size=(1600, 600), alpha=160):
        self.size = size
        self.alpha = alpha
        self.themeManager = themeManager
        # Semi-transparent background surface
        self.bg_surface = pg.Surface(self.size)
        self.bg_surface.set_alpha(self.alpha)
        # Opaque surface for text and icons
        self.text_surface = pg.Surface(self.size, pg.SRCALPHA)


    def _resetSurfaces(self):
        self.bg_surface.fill(self.themeManager.getAccentColor())
        self.text_surface.fill((0, 0, 0, 0))


    def draw(self, display, game):
        self._resetSurfaces()

        font_name = self.themeManager.fontName
        text_color = self.themeManager.current["colors"]["text"]
        canvas = _Canvas(self.size)

        font_large = pg.font.SysFont(font_name, 70)
        title = font_large.render(f"Victoire du Joueur {game.winner} !", True, text_color)
        self.text_surface.blit(title, Position(canvas, (50, 25)).get(title.get_size()))

        font_small = pg.font.SysFont(font_name, 45)
        lines = [
            (font_small.render("Temps moyen pour jouer :", True, text_color), 40),
            (font_small.render(f"Joueur 1: {round(game.timerHistory[0][1], 2)}s", True, text_color), 50),
            (font_small.render(f"Joueur 2: {round(game.timerHistory[1][1], 2)}s", True, text_color), 60),
        ]
        for surface, y_pct in lines:
            self.text_surface.blit(surface, Position(canvas, (50, y_pct)).get(surface.get_size()))

        display.blit(self.bg_surface, (0, 150))
        display.blit(self.text_surface, (0, 150))