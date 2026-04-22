import pygame as pg
from pygame.locals import *
from enum import Enum


class GameMode(Enum):
    PVP = 1
    PVE = 2


from src.Game.Window import DisplayedWindow
from src.Game.Board import BoardParam
from src.AI.GomokuAI import GomokuAI
from src.Game.Timer import Timer

from src.Game.GameState import GameState


class Game:
    def __init__(self):
        self.activePlayer = 1               # 1: Player 1, 2: Player 2
        self.mode = None                    # GameMode.PVP or GameMode.PVE
        self.currentScore = {1: 0, 2: 0}
        self.winner = 0

        self.state = GameState(BoardParam.NUM_CASE)

        self.stonesLocations = []           # list of tuple for each piece on the board: (row, col)
        self.moveHistory = []               # list of (player, row, col) tuples for each move
        self.timerHistory = []              # list of (player, time) tuples for each move
        self.timer = Timer()
        self.gomokuAI = GomokuAI()
        self.isActive = True
        self.hoverCell = None
        self.proposedMove = None


    @property
    def boardState(self):
        return self.state.grid


    def _checkFiveInARow(self, row: int, col: int):
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:  # horizontal, vertical, diagonal down-right, diagonal down-left
            count = 1  # count the piece just placed
            # check in the positive direction
            r, c = row + dr, col + dc
            while 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE and self.state.grid[r][c] == self.activePlayer:
                count += 1
                r += dr
                c += dc

            # check in the negative direction
            r, c = row - dr, col - dc
            while 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE and self.state.grid[r][c] == self.activePlayer:
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
        if any(0 in row for row in self.state.grid):
            return False

        if self.currentScore[1] == self.currentScore[2]:
            self.winner = 0
        else:
            self.winner = max(self.currentScore, key=self.currentScore.get)
        return True


    def _placePiece(self, row: int, col: int):
        self.state.play(row, col, self.activePlayer)
        self.stonesLocations.append((row, col))


    def _handleCapture(self, row: int, col: int):
        opponent = 2 if self.activePlayer == 1 else 1
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:  # all 8 directions
            r1, c1 = row + dr, col + dc
            r2, c2 = row + 2*dr, col + 2*dc
            r3, c3 = row + 3*dr, col + 3*dc

            if (0 <= r3 < BoardParam.NUM_CASE and 0 <= c3 < BoardParam.NUM_CASE
                and self.state.grid[r1][c1] == opponent
                and self.state.grid[r2][c2] == opponent
                and self.state.grid[r3][c3] == self.activePlayer):
                
                # capture detected
                self.state.undo(r1, c1)
                self.state.undo(r2, c2)
                self.currentScore[self.activePlayer] += 2

                # remove captured pieces from stonesLocation
                self.stonesLocations = [(r, c) for (r, c) in self.stonesLocations if (r, c) != (r1, c1) and (r, c) != (r2, c2)]


    def _checkDoubleThree(self, row: int, col: int):
        patterns = [".XXX..", "..XXX.", ".X.XX.", ".XX.X."]
        free_three_count = 0

        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line_str = ""
            for i in range(-4, 5):
                r, c = row + i * dr, col + i * dc
                if i == 0:
                    line_str += "X"
                elif 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE:
                    val = self.state.grid[r][c]
                    if val == 0:
                        line_str += "."
                    elif val == self.activePlayer:
                        line_str += "X"
                    else:
                        line_str += "O"
                else:
                    line_str += "O"

            if any(p in line_str for p in patterns):
                free_three_count += 1

        return free_three_count >= 2


    def _checkValidMove(self, row: int, col: int):
        if self.state.grid[row][col] != 0 or self._checkDoubleThree(row, col):
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
        self.isActive = False
        window.displayedWindow = DisplayedWindow.GAME_OVER


    def _handleMove(self, row: int, col: int, window):
        if self._checkValidMove(row, col):
            self._placePiece(row, col)
            self._handleCapture(row, col)
            self.moveHistory.append((self.activePlayer, row, col))
            self.timerHistory.append((self.activePlayer, self.timer.getElapsedTime()))
            self.hoverCell = None
            self.proposedMove = None

            if self._checkWinCondition(row, col) or self._checkTieCondition():
                self._endGame(window)

            self.activePlayer = 2 if self.activePlayer == 1 else 1
            self.timer.start()


# Public methods
    def init(self, gameMode: GameMode):
        self.isActive = True
        self.activePlayer = 1
        self.mode = gameMode
        self.currentScore = {1: 0, 2: 0}
        self.state = GameState(BoardParam.NUM_CASE)
        self.stonesLocations = []
        self.moveHistory = []
        self.timerHistory = []
        self.hoverCell = None
        self.proposedMove = None
        self.timer.reset()
        self.timer.start()


    def test_undo(self, window):                                                # <== A SUPPRIMER
        print("=== TEST UNDO ===")

        self._handleMove(7, 7, window)
        self.state.debug_state()

        self.state.undo(7, 7)
        self.state.grid[7][7] = 0

        print("After undo:")
        self.state.debug_state()


    def update(self, event: pg.event.Event, window):
        if self.mode == GameMode.PVE and self.activePlayer == 2:
            # TODO: maybe start AI timer here if too slow
            AIMove = self.gomokuAI.findBestMove(self.state, False)
            self._handleMove(AIMove[0], AIMove[1], window)

        if event.type == MOUSEMOTION:
            row, col = window.board.getIndexFromPos(window, event.pos)
            if row is not None and col is not None:
                self.hoverCell = (row, col)
            else:
                self.hoverCell = None

        if event.type == MOUSEBUTTONDOWN:
            gameMove = window.board.getIndexFromPos(window, event.pos)
            if gameMove[0] is not None and gameMove[1] is not None:
                self._handleMove(gameMove[0], gameMove[1], window)

        if event.type == pg.KEYDOWN:                                            # <== A SUPPRIMER
            if event.key == pg.K_u:
                self.test_undo(window)
