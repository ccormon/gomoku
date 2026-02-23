import pygame as pg
from pygame.locals import *

from Game import Game, GameMode
from Window import DisplayedWindow
from Button import Button, ToggleButton
import themes
from ThemeManager import ThemeManager


class ButtonClickHandler:
    def __init__(self, game: Game, window):
        self.game = game
        self.window = window
        self.themeManager = window.themeManager
        self.soundEffects = window.soundEffects
        self.musicPlayer = window.musicPlayer

    def homeButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.displayedWindow = DisplayedWindow.MAIN_MENU


    def exitButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        pg.quit()
        exit()


    def musicButtonClick(self, button: ToggleButton):
        self.soundEffects.play_sound("pop")
        if button.active:
            self.musicPlayer.unpause()
        else:
            self.musicPlayer.pause()


    def soundButtonClick(self, button: ToggleButton):
        self.soundEffects.toggle()
        self.soundEffects.play_sound("pop")


    def playButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.displayedWindow = DisplayedWindow.GAME_SCENE


    def settingButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        match self.window.displayedWindow:
            case DisplayedWindow.MAIN_MENU:
                self.window.displayedWindow = DisplayedWindow.SETTINGS
            case DisplayedWindow.SETTINGS:
                self.window.displayedWindow = DisplayedWindow.MAIN_MENU


    def pvpButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.game.init(gameMode=GameMode.PVP)
        self.window.displayedWindow = DisplayedWindow.GAME_SCENE


    def pveButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.game.init(gameMode=GameMode.PVE)
        self.window.displayedWindow = DisplayedWindow.GAME_SCENE


    def theme1ButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.themeManager.setTheme("classic")


    def theme2ButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.themeManager.setTheme("crystal")


    def theme3ButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.themeManager.setTheme("bakery")


    def theme4ButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        self.window.themeManager.setTheme("rat")