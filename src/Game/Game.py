import pygame as pg
from pygame.locals import *
from enum import Enum


class GameMode(Enum):
    PVP = 1
    PVE = 2


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
        self.aiTimerHistory = []            # actual AI search durations (not event-loop delay)
        self.timer = Timer()
        self.gomokuAI = GomokuAI()
        self.lastAITime = 0.0
        self.isActive = True
        self.hoverCell = None
        self.proposedMove = None


    @property
    def boardState(self):
        return self.state.grid


    @property
    def turnNumber(self):
        """Number of completed rounds (one move by each player)."""
        return len(self.moveHistory) // 2


    @property
    def lastMove(self):
        return self.moveHistory[-1][1:] if self.moveHistory else None


    @property
    def averageAITime(self):
        if not self.aiTimerHistory:
            return 0.0
        return sum(self.aiTimerHistory) / len(self.aiTimerHistory)


    def averageMoveTime(self, player: int):
        """Return a meaningful mean: search time for the AI, turn time for humans."""
        if self.mode == GameMode.PVE and player == 2:
            return self.averageAITime
        times = [elapsed for owner, elapsed in self.timerHistory if owner == player]
        return sum(times) / len(times) if times else 0.0


    def playerName(self, player: int):
        return "IA" if self.mode == GameMode.PVE and player == 2 else f"Joueur {player}"


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


    def _hasAnyFive(self, player: int):
        for row in range(BoardParam.NUM_CASE):
            for col in range(BoardParam.NUM_CASE):
                if self.state.grid[row][col] != player:
                    continue
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    if all(
                        0 <= row + step * dr < BoardParam.NUM_CASE
                        and 0 <= col + step * dc < BoardParam.NUM_CASE
                        and self.state.grid[row + step * dr][col + step * dc] == player
                        for step in range(5)
                    ):
                        return True
        return False


    def _captureCells(self, row: int, col: int, player: int):
        opponent = 2 if player == 1 else 1
        captured = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            positions = [(row + step * dr, col + step * dc) for step in range(1, 4)]
            if not all(0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE for r, c in positions):
                continue
            first, second, anchor = positions
            if (self.state.grid[first[0]][first[1]] == opponent
                    and self.state.grid[second[0]][second[1]] == opponent
                    and self.state.grid[anchor[0]][anchor[1]] == player):
                captured.extend((first, second))
        return list(dict.fromkeys(captured))


    def _canBreakAlignmentOrWinByCapture(self, alignedPlayer: int):
        defender = 2 if alignedPlayer == 1 else 1
        for row in range(BoardParam.NUM_CASE):
            for col in range(BoardParam.NUM_CASE):
                if self.state.grid[row][col] != 0:
                    continue
                captured = self._captureCells(row, col, defender)
                if not captured:
                    continue
                self.state.grid[row][col] = defender
                previous = [(r, c, self.state.grid[r][c]) for r, c in captured]
                for r, c, _ in previous:
                    self.state.grid[r][c] = 0
                winsByCapture = self.currentScore[defender] + len(captured) >= 10
                breaksAlignment = not self._hasAnyFive(alignedPlayer)
                for r, c, value in previous:
                    self.state.grid[r][c] = value
                self.state.grid[row][col] = 0
                if winsByCapture or breaksAlignment:
                    return True
        return False


    def _checkWinCondition(self, row: int, col: int):
        if self.currentScore[self.activePlayer] >= 10:
            self.winner = self.activePlayer
            return True
        opponent = 2 if self.activePlayer == 1 else 1
        if self._hasAnyFive(opponent):
            self.winner = opponent
            return True
        if self._checkFiveInARow(row, col) and not self._canBreakAlignmentOrWinByCapture(self.activePlayer):
            self.winner = self.activePlayer
            return True
        return False


    def _checkTieCondition(self):
        if any(0 in row for row in self.state.grid):
            return False

        self.winner = 0
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
        return self._checkDoubleThreeForPlayer(row, col, self.activePlayer)


    def _checkDoubleThreeForPlayer(self, row: int, col: int, player: int):
        if self.state.grid[row][col] != 0 or self._captureCells(row, col, player):
            return False
        freeThreeCount = 0
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            values = []
            for offset in range(-5, 6):
                r, c = row + offset * dr, col + offset * dc
                values.append(self.state.grid[r][c] if 0 <= r < BoardParam.NUM_CASE and 0 <= c < BoardParam.NUM_CASE else 3)
            values[5] = player
            directionHasThree = False
            for completion in range(1, 10):
                if completion == 5 or values[completion] != 0:
                    continue
                values[completion] = player
                for start in range(6):
                    if (values[start] == 0 and values[start + 5] == 0
                            and all(values[cell] == player for cell in range(start + 1, start + 5))
                            and start < 5 < start + 5
                            and start < completion < start + 5):
                        directionHasThree = True
                        break
                values[completion] = 0
                if directionHasThree:
                    break
            freeThreeCount += directionHasThree
        return freeThreeCount >= 2


    def _checkValidMove(self, row: int, col: int):
        if not (0 <= row < BoardParam.NUM_CASE and 0 <= col < BoardParam.NUM_CASE):
            return False
        if self.state.grid[row][col] != 0 or self._checkDoubleThree(row, col):
            return False
        return True


    def findAIMove(self, player: int):
        self.lastAITime = 0.0
        try:
            move = self.gomokuAI.findBestMove(self.state, player, self.currentScore)
            self.lastAITime = self.gomokuAI.last_search.elapsed_seconds
            if move is not None and self._checkValidMove(move[0], move[1]):
                return move
        except (MemoryError, RuntimeError, ValueError):
            pass

        center = BoardParam.NUM_CASE // 2
        candidates = (
            (row, col)
            for row in range(BoardParam.NUM_CASE)
            for col in range(BoardParam.NUM_CASE)
        )
        return min(
            (move for move in candidates if self._checkValidMove(move[0], move[1])),
            key=lambda move: abs(move[0] - center) + abs(move[1] - center),
            default=None,
        )


    def _endGame(self, window):
        from src.Game.Window import DisplayedWindow

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
            window.soundEffects.play_sound("piece")
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
        self.aiTimerHistory = []
        self.hoverCell = None
        self.proposedMove = None
        self.lastAITime = 0.0
        self.timer.reset()
        self.timer.start()


    def update(self, event: pg.event.Event, window):
        if self.mode == GameMode.PVE and self.activePlayer == 2:
            AIMove = self.findAIMove(2)
            if AIMove is not None:
                self.aiTimerHistory.append(self.lastAITime)
                self._handleMove(AIMove[0], AIMove[1], window)
            return

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
