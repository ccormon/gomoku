import pygame as pg
from pygame.locals import *
from enum import Enum


class GameMode(Enum):
    PVP = 1
    PVE = 2


from Window import DisplayedWindow
from Board import BoardParam
from GomokuAI import GomokuAI
from Timer import Timer


class Game:
    def __init__(self):
        self.activePlayer = 1               # 1: Player 1, 2: Player 2
        self.mode = None                    # GameMode.PVP or GameMode.PVE
        self.currentScore = {1: 0, 2: 0}
        self.winner = 0

        self.boardState = [[0 for _ in range(BoardParam.NUM_CASE)] for _ in range(BoardParam.NUM_CASE)] # 0: empty, 1: player1 piece, 2: player2 piece
        self.moveHistory = []               # list of (player, row, col) tuples for each move
        self.timerHistory = []              # list of (player, time) tuples for each move
        self.timer = Timer()
        self.gomokuAI = GomokuAI()


    def _checkFiveInARow(self, row: int, col: int):
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
            self.winner = self.activePlayer
            return True
        return False


    def _checkTieCondition(self):
        if any(0 in row for row in self.boardState):
            return False

        if self.currentScore[1] == self.currentScore[2]:
            self.winner = 0
        else:
            self.winner = max(self.currentScore, key=self.currentScore.get)
        return True


    def _placePiece(self, row: int, col: int):
        self.boardState[row][col] = self.activePlayer


    def _handleCapture(self, row: int, col: int):
        opponent = 2 if self.activePlayer == 1 else 1
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:  # all 8 directions
            r1, c1 = row + dr, col + dc
            r2, c2 = row + 2*dr, col + 2*dc
            r3, c3 = row + 3*dr, col + 3*dc

            if (0 <= r3 < BoardParam.NUM_CASE and 0 <= c3 < BoardParam.NUM_CASE
                and self.boardState[r1][c1] == opponent
                and self.boardState[r2][c2] == opponent
                and self.boardState[r3][c3] == self.activePlayer):
                
                # capture detected
                self.boardState[r1][c1] = 0
                self.boardState[r2][c2] = 0
                self.currentScore[self.activePlayer] += 2


    def _checkValidMove(self, row: int, col: int):
        # TODO: check if the move is valid (not placing on an occupied space, not violating opening rules, ...)
        if self.boardState[row][col] != 0:
            return False
        return True


    def _endGame(self, window):
        '''
        # print winner and scores + mean time per move for each player
        print(f"Game Over! Winner: {'Tie' if self.winner == 0 else 'Player ' + str(self.winner)}")
        print(f"Final Score: Player 1: {self.currentScore[1]}, Player 2: {self.currentScore[2]}")
        player1Times = [time for player, time in self.timerHistory if player == 1]
        player2Times = [time for player, time in self.timerHistory if player == 2]
        print(f"Average Time per Move: Player 1: {sum(player1Times)/len(player1Times) if player1Times else 0:.2f} seconds, Player 2: {sum(player2Times)/len(player2Times) if player2Times else 0:.2f} seconds")
        '''
        window.displayedWindow = DisplayedWindow.GAME_OVER


    def _handleMove(self, row: int, col: int, window):
        if self._checkValidMove(row, col):
            self._placePiece(row, col)
            self._handleCapture(row, col)
            self.moveHistory.append((self.activePlayer, row, col))
            self.timerHistory.append((self.activePlayer, self.timer.getElapsedTime()))

            if self._checkWinCondition(row, col) or self._checkTieCondition():
                self._endGame(window)

            self.activePlayer = 2 if self.activePlayer == 1 else 1
            self.timer.start()


# Public methods
    def init(self, gameMode: GameMode):
        self.activePlayer = 1
        self.mode = gameMode
        self.currentScore = {1: 0, 2: 0}
        self.boardState = [[0 for _ in range(BoardParam.NUM_CASE)] for _ in range(BoardParam.NUM_CASE)]
        self.timer.reset()
        self.timer.start()


    def update(self, event: pg.event.Event, window):
        if self.mode == GameMode.PVE and self.activePlayer == 2:
            # TODO: maybe start AI timer here if too slow
            AIMove = self.gomokuAI.findBestMove(self, False)
            self._handleMove(AIMove[0], AIMove[1])

        if event.type == MOUSEBUTTONDOWN:
            gameMove = window.board.getIndexFromPos(window, event.pos)
            if gameMove[0] is not None and gameMove[1] is not None:
                self._handleMove(gameMove[0], gameMove[1], window)