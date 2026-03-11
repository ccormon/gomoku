import pygame as pg
from pygame.locals import *

from src.Game.Game import Game, GameMode
from src.Game.Window import DisplayedWindow
from src.Game.Button import Button, ToggleButton
import src.Game.themes
from src.Game.ThemeManager import ThemeManager


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


    def scoreButtonClick(self, button: Button):
        self.soundEffects.play_sound("pop")
        # download a file with the score and metrics of the game
        with open("score.txt", "w") as f:
            f.write("Gomoku - Score et métriques de la partie\n")
            f.write(f"Gagnant : Joueur {self.game.winner}\n")
            f.write(f"Mode de jeu : {'PVP' if self.game.mode == GameMode.PVP else 'PVE'}\n")
            f.write(f"Nombre de coups : {len(self.game.moveHistory)}\n")
            f.write(f"Score final : Joueur 1: {self.game.currentScore[1]} - Joueur 2: {self.game.currentScore[2]}\n")
            f.write(f"Temps moyen pour jouer : Joueur 1: {round(self.game.timerHistory[0][1], 2)}s, Joueur 2: {round(self.game.timerHistory[1][1], 2)}s\n")
            f.write("Historique des coups :\n")
            for i, move in enumerate(self.game.moveHistory):
                player, row, col = move
                time = self.game.timerHistory[i][1]
                f.write(f"Joueur {player} a joué en ({row}, {col}) après {round(time, 2)}s\n")
        
        button.active = False


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