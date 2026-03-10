import pygame as pg
from pygame.locals import *

# TODO: is it useful ? for now it's just a list

class GameHistory:
    def __init__(self):
        self.history = []

    def reset(self):
        self.history = []
    
    def addMove(self, player: int, row: int, col: int):
        self.history.append((player, row, col))
    
    def undoMove(self):
        if self.history:
            return self.history.pop()
        return None
