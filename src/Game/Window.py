import pygame as pg
from pygame.locals import *
from enum import Enum


class DisplayedWindow(Enum):
    MAIN_MENU = 1
    GAME_SCENE = 2
    SETTINGS = 3
    GAME_OVER = 4


from src.Game.Game import Game
import src.Game.themes as themes
from src.Game.ThemeManager import ThemeManager
from src.Game.Button import Button, ToggleButton
from src.Game.Slider import Slider
from src.Game.ButtonClickHandler import ButtonClickHandler
from src.Game.MusicPlayer import MusicPlayer
from src.Game.SoundEffects import SoundEffects
from src.Game.PlayerIcon import PlayerIcon
from src.Game.Position import Position, PositionUnit, PositionReference
from src.Game.assets import Assets
from src.Game.Board import Board
from src.Game.Overlay import Overlay


class Window:
    def __init__(self, game):
        self.game = game
        self.size = (1600, 900)
        self.fps = 30
        self.displayedWindow = DisplayedWindow.MAIN_MENU
        self.display = self._createDisplay("Gomoku", Assets.ICON)

        self.soundEffects = SoundEffects()
        self.musicPlayer = MusicPlayer()
        self.themeManager = ThemeManager(themes.THEMES, self, default="flower")
        self.board = Board()
        self.overlay = Overlay(self.themeManager)

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
        self.scoreButton = Button(Assets.SCORE, Position(self, (71, 69.5)), buttonClick.scoreButtonClick)

        self.musicButton = ToggleButton(Assets.MUSIC_ON, Assets.MUSIC_OFF, Position(self, (37, 28)), True, buttonClick.musicButtonClick)
        self.soundButton = ToggleButton(Assets.SOUND_ON, Assets.SOUND_OFF, Position(self, (37, 38)), True, buttonClick.soundButtonClick)

        self.musicVolumeSlider = Slider(self, (52, 28), 25, 1.0,
                                        lambda v: self.musicPlayer.set_volume(v))
        self.soundVolumeSlider = Slider(self, (52, 38), 25, 1.0,
                                        lambda v: self.soundEffects.set_volume(v))
        
        self.pvpButton = Button(Assets.PVP, Position(self, (37, 57)), buttonClick.pvpButtonClick, hoverFactor=1.05)
        self.pveButton = Button(Assets.PVE, Position(self, (63, 57)), buttonClick.pveButtonClick, hoverFactor=1.05)

        self.theme1Button = Button(Assets.THEME1, Position(self, (41, 61)), buttonClick.theme1ButtonClick, False)
        self.theme2Button = Button(Assets.THEME2, Position(self, (59, 61)), buttonClick.theme2ButtonClick, False)
        self.theme3Button = Button(Assets.THEME3, Position(self, (41, 82)), buttonClick.theme3ButtonClick, False)
        self.theme4Button = Button(Assets.THEME4, Position(self, (59, 82)), buttonClick.theme4ButtonClick, False)


    def _drawBackground(self):
        background = self.themeManager.getBackground()
        self.display.blit(pg.transform.scale(background, self.size), (0, 0))


    def _drawMainMenu(self):
        self._drawBackground()

        # TODO: put text rendering in a separate method or a separate class
        font = pg.font.SysFont(self.themeManager.fontName, 90)
        title = font.render("Gomoku", True, (255, 255, 255))
        self.display.blit(title, Position(self, (50, 17)).get((title.get_width(), 0)))
        
        font = pg.font.SysFont(self.themeManager.fontName, 50)
        selectModeText = font.render("Sélectionnez un mode de jeu :", True, (255, 255, 255))
        self.display.blit(selectModeText, Position(self, (50, 37)).get((selectModeText.get_width(), 0)))

        self.pvpButton.draw(self.display)
        self.pveButton.draw(self.display)

        self.exitButton.draw(self.display)
        self.settingButton.draw(self.display)


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
        self.display.blit(score, Position(self, (50, 3)).get((score.get_width(), 0)))


    def _drawSettingsMenu(self):
        self._drawBackground()

        title_font = pg.font.SysFont(self.themeManager.fontName, 100)
        title = title_font.render("Options", True, (255, 255, 255))
        self.display.blit(title, Position(self, (50, 10)).get((title.get_width(), 0)))
        
        label_font = pg.font.SysFont(self.themeManager.fontName, 40)
        # TODO: put music/sound settings in a separate method
        # --- Music row ---
        #music_label = label_font.render("Music", True, (255, 255, 255))
        #music_label_y = int(self.size[1] * 0.48) - music_label.get_height() // 2
        #self.display.blit(music_label, (int(self.size[0] * 0.18), music_label_y))
        self.musicButton.draw(self.display)
        self.musicVolumeSlider.draw(self.display)
        #music_pct = label_font.render(f"{int(self.musicVolumeSlider.value * 100)}%", True, (255, 255, 255))
        #self.display.blit(music_pct, (int(self.size[0] * 0.76), music_label_y))

        # --- Sound row ---
        #sound_label = label_font.render("Sound", True, (255, 255, 255))
        #sound_label_y = int(self.size[1] * 0.62) - sound_label.get_height() // 2
        #self.display.blit(sound_label, (int(self.size[0] * 0.18), sound_label_y))
        self.soundButton.draw(self.display)
        self.soundVolumeSlider.draw(self.display)
        #sound_pct = label_font.render(f"{int(self.soundVolumeSlider.value * 100)}%", True, (255, 255, 255))
        #self.display.blit(sound_pct, (int(self.size[0] * 0.76), sound_label_y))

        self.settingButton.draw(self.display)
        self.exitButton.draw(self.display)

        # Theme selection text using Position
        theme_label = label_font.render("Sélection du thème :", True, (255, 255, 255))
        self.display.blit(theme_label, Position(self, (50, 45)).get((theme_label.get_width(), 0)))

        self.theme1Button.draw(self.display)
        self.theme2Button.draw(self.display)
        self.theme3Button.draw(self.display)
        self.theme4Button.draw(self.display)


    def _drawGameOverScreen(self):
        self._drawGameScene()
        self.overlay.draw(self.display, self.game)
        self.scoreButton.draw(self.display)


# Public methods
    def refreshDisplay(self):
        match self.displayedWindow:
            case DisplayedWindow.MAIN_MENU:
                self._drawMainMenu()
            case DisplayedWindow.GAME_SCENE:
                self._drawGameScene()
            case DisplayedWindow.SETTINGS:
                self._drawSettingsMenu()
            case DisplayedWindow.GAME_OVER:
                self._drawGameOverScreen()
        pg.display.flip()


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
        self.musicVolumeSlider.update(event)
        self.soundVolumeSlider.update(event)
        self.theme1Button.update(event)
        self.theme2Button.update(event)
        self.theme3Button.update(event)
        self.theme4Button.update(event)
        self.settingButton.update(event)
        self.exitButton.update(event)


    def updateGameOver(self, event: pg.event.Event):
        self.homeButton.update(event)
        self.exitButton.update(event)
        self.scoreButton.update(event)