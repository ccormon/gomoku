import pygame as pg
from pygame.locals import *
from enum import Enum
import threading

class GameMode(Enum):
    PVP = 1
    PVE = 2

from Board import BoardParam
from GomokuAI import GomokuAI

class Game:
    def __init__(self):
        self.activePlayer = 1               # 1: Player 1, 2: Player 2
        self.mode = None                    # GameMode.PVP or GameMode.PVE
        self.currentScore = {1: 0, 2: 0}
        self.timerP1 = 0
        self.timerP2 = 0

        self.boardState = [[0 for _ in range(BoardParam.NUM_CASE)] for _ in range(BoardParam.NUM_CASE)] # 0: empty, 1: player1 piece, 2: player2 piece
        self.gomokuAI = GomokuAI()

    def _placePiece(self, row: int, col: int):
        self.boardState[row][col] = self.activePlayer


    def _checkFiveInARow(self, row: int, col: int):
        # check if the last move resulted in 5 pieces in a row for the active player
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:  # horizontal, vertical, diagonal down-right, diagonal down-left
            count = 1  # count the piece just placed
            # check in the positive direction
            r, c = row + dr, col + dc
            while 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE and self.boardState[r][c] == self.activePlayer:
                count += 1
                r += dr
                c += dc

            # check in the negative direction
            r, c = row - dr, col - dc
            while 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE and self.boardState[r][c] == self.activePlayer:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True


    def _checkWinCondition(self, row: int, col: int):
        if self._checkFiveInARow(row, col) or self.currentScore[self.activePlayer] >= 10:
            return True
        return False


    def _checkTieCondition(self):
        # check if the board is full
        if any(0 in row for row in self.boardState):
            return False
        return True


    def _handleCapture(self, row: int, col: int):
        # check if the last move resulted in a capture
        




        '''
        self._capturePieces(row, col)
        if self.activePlayer == 1:
            self.currentScore[1] += 2
        else:
            self.currentScore[2] += 2
            '''
        pass


    def _checkValidMove(self, row: int, col: int):
        # check if the move is valid according to the game rules (e.g., not placing on an occupied space, not violating opening rules)
        if self.boardState[row][col] != 0:
            return False
        return True


    def _handleMove(self, row: int, col: int):
        if self._checkValidMove(row, col):
            self._placePiece(row, col)
            #self.history.append((row, col, self.activePlayer))
            self._handleCapture(row, col)
            if self._checkWinCondition(row, col):
                print (f"Player {self.activePlayer} wins!")
            '''
            elif self._checkTieCondition():
                winner = max(self.currentScore, key=self.currentScore.get)
                # handle tie condition
                pass
            '''
            self.activePlayer = 2 if self.activePlayer == 1 else 1


# Public methods
    def init(self, gameMode: GameMode):
        self.activePlayer = 1
        self.mode = gameMode
        self.currentScore = {1: 0, 2: 0}
        self.boardState = [[0 for _ in range(BoardParam.NUM_CASE)] for _ in range(BoardParam.NUM_CASE)]


    def update(self, event: pg.event.Event, window):
        if self.mode == GameMode.PVE and self.activePlayer == 2:
            # start AI timer
            AIMove = self.gomokuAI.findBestMove(self, False)
            # stop AI timer
            self._handleMove(AIMove[0], AIMove[1])

        # start timer for active player
        if event.type == MOUSEBUTTONDOWN:
            gameMove = window.board.getIndexFromPos(window, event.pos)
            if gameMove[0] is not None and gameMove[1] is not None:
                # stop timer for active player -> what happens if the move is invalid? should the timer continue until a valid move is made?
                self._handleMove(gameMove[0], gameMove[1])
