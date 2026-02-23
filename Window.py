import pygame as pg
from pygame.locals import *
from enum import Enum

class DisplayedWindow(Enum):
    MAIN_MENU = 1
    GAME_SCENE = 2
    SETTINGS = 3

import themes
from ThemeManager import ThemeManager
from Button import Button, ToggleButton
from ButtonClickHandler import ButtonClickHandler
from MusicPlayer import MusicPlayer
from PlayerIcon import PlayerIcon
from Position import Position, PositionUnit, PositionReference
from SoundEffects import SoundEffects
from assets import Assets
from Board import Board
from Game import Game


class Window:
    def __init__(self, game):
        self.game = game
        self.size = (1600, 900)
        self.fps = 30
        self.displayedWindow = DisplayedWindow.MAIN_MENU
        self.display = self._createDisplay("Gomoku", Assets.ICON)

        self.soundEffects = SoundEffects()
        self.musicPlayer = MusicPlayer()
        self.themeManager = ThemeManager(themes.THEMES, self, default="classic")
        self.board = Board()

        self.player1Icon = PlayerIcon(self.themeManager, self.game, (self.size[0] // 2 - 300, 30), (100, 100), 1)
        self.player2Icon = PlayerIcon(self.themeManager, self.game, (self.size[0] // 2 + 200, 30), (100, 100), 2)

        self._setButtons()
        self._drawMainMenu()


    def _createDisplay(self, name: str, iconPath: str):
        display = pg.display.set_mode(self.size)
        pg.display.set_caption(name)
        icon = pg.image.load(iconPath).convert_alpha()
        pg.display.set_icon(icon)
        return display


    def _setButtons(self):
        buttonClick = ButtonClickHandler(self.game, self)

        self.exitButton = Button(Assets.EXIT, Position(self, (96, 5)), buttonClick.exitButtonClick)
        self.settingButton = Button(Assets.SETTINGS, Position(self, (92, 5)), buttonClick.settingButtonClick)
        self.homeButton = Button(Assets.HOME, Position(self, (92, 5)), buttonClick.homeButtonClick)

        self.musicButton = ToggleButton(Assets.MUSIC_ON, Assets.MUSIC_OFF, Position(self, (50, 50)), True, buttonClick.musicButtonClick)
        self.soundButton = ToggleButton(Assets.SOUND_ON, Assets.SOUND_OFF, Position(self, (50, 60)), True, buttonClick.soundButtonClick)
        
        self.pvpButton = Button(Assets.PVP, Position(self, (33, 50)), buttonClick.pvpButtonClick)
        self.pveButton = Button(Assets.PVE, Position(self, (66, 50)), buttonClick.pveButtonClick)

        self.theme1Button = Button(Assets.THEME1, Position(self, (37, 67)), buttonClick.theme1ButtonClick, False)
        self.theme2Button = Button(Assets.THEME2, Position(self, (67, 67)), buttonClick.theme2ButtonClick, False)
        self.theme3Button = Button(Assets.THEME3, Position(self, (37, 80)), buttonClick.theme3ButtonClick, False)
        self.theme4Button = Button(Assets.THEME4, Position(self, (67, 80)), buttonClick.theme4ButtonClick, False)


    def _drawBackground(self):
        background = self.themeManager.getBackground()
        self.display.blit(pg.transform.scale(background, self.size), (0, 0))


    def _drawMainMenu(self):
        self._drawBackground()

        font = pg.font.SysFont(self.themeManager.fontName, 90)
        title = font.render("Gomoku", True, (255, 255, 255))
        self.display.blit(title, (self.size[0] // 2 - title.get_width() // 2, 100))
        font = pg.font.SysFont(self.themeManager.fontName, 50)
        selectModeText = font.render("Select Game Mode:", True, (255, 255, 255))
        self.display.blit(selectModeText, (self.size[0] // 2 - selectModeText.get_width() // 2, 300))

        self.pvpButton.draw(self.display)
        self.pveButton.draw(self.display)

        self.exitButton.draw(self.display)
        self.settingButton.draw(self.display)

        pg.display.flip()


    def _drawGameScene(self):
        self._drawBackground()
        self.board.draw(self)

        self.exitButton.draw(self.display)
        self.homeButton.draw(self.display)

        self.player1Icon.draw(self.display)
        self.player2Icon.draw(self.display)

        # print scores
        font = pg.font.SysFont(self.themeManager.fontName, 90)
        score = font.render(f"{self.game.currentScore[1]} | {self.game.currentScore[2]}", True, (255, 255, 255))
        self.display.blit(score, (self.size[0] // 2 - score.get_width() // 2, 30))

        pg.display.flip()


    def _drawSettingsMenu(self):
        self._drawBackground()

        font = pg.font.SysFont(self.themeManager.fontName, 100)
        title = font.render("Settings", True, (255, 255, 255))
        self.display.blit(title, (self.size[0] // 2 - title.get_width() // 2, 100))

        self.musicButton.draw(self.display)
        self.soundButton.draw(self.display)

        self.settingButton.draw(self.display)
        self.exitButton.draw(self.display)

        self.theme1Button.draw(self.display)
        self.theme2Button.draw(self.display)
        self.theme3Button.draw(self.display)
        self.theme4Button.draw(self.display)

        pg.display.flip()


# Public methods
    def refreshDisplay(self):
        match self.displayedWindow:
            case DisplayedWindow.MAIN_MENU:
                self._drawMainMenu()
            case DisplayedWindow.GAME_SCENE:
                self._drawGameScene()
            case DisplayedWindow.SETTINGS:
                self._drawSettingsMenu()


    # Update methods for each window, called from event handler
    def updateMainMenu(self, event: pg.event.Event):
        self.pvpButton.update(event)
        self.pveButton.update(event)
        self.settingButton.update(event)
        self.exitButton.update(event)


    def updateGameScene(self, event: pg.event.Event):
        self.homeButton.update(event)
        self.exitButton.update(event)
        self.game.update(event, self)


    def updateSettingsMenu(self, event: pg.event.Event):
        self.musicButton.update(event)
        self.soundButton.update(event)
        self.theme1Button.update(event)
        self.theme2Button.update(event)
        self.theme3Button.update(event)
        self.theme4Button.update(event)
        self.settingButton.update(event)
        self.exitButton.update(event)