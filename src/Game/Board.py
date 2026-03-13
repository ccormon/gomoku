import pygame as pg
from pygame.locals import *

from src.Game.ThemeManager import ThemeManager
from src.Game.Position import Position, PositionUnit, PositionReference


class BoardParam:
    SIZE = 722
    Y_OFFSET = 150
    NUM_CASE = 19
    CASE_SIZE = SIZE // NUM_CASE
    BORDER_SIZE = SIZE - CASE_SIZE


class Board:
    def __init__(self):
        self.boardState = None
        self.themeManager = None
        self.color = (0, 0, 0)
        self.lineWidth = 2
        self.circleRadius = 7
        self.hoverAlpha = 120


    def _boardOrigin(self, window):
        return (
            window.size[0] // 2 - BoardParam.SIZE // 2,
            BoardParam.Y_OFFSET
            )


    def _boardBorderOrigin(self, window):
        return (
            self._boardOrigin(window)[0] + (BoardParam.CASE_SIZE // 2),
            self._boardOrigin(window)[1] + (BoardParam.CASE_SIZE // 2)
            )


    def getIndexFromPos(self, window, pos: tuple):
        boardOrigin = self._boardOrigin(window)
        x_rel = pos[0] - boardOrigin[0]
        y_rel = pos[1] - boardOrigin[1]
        if 0 <= x_rel < BoardParam.SIZE and 0 <= y_rel < BoardParam.SIZE:
            col = int(x_rel // BoardParam.CASE_SIZE)
            row = int(y_rel // BoardParam.CASE_SIZE)
            return (row, col)
        return (None, None)


    def _getPosFromIndex(self, row: int, col: int, window):
        boardBorderOrigin = self._boardBorderOrigin(window)
        x = boardBorderOrigin[0] + col * BoardParam.CASE_SIZE
        y = boardBorderOrigin[1] + row * BoardParam.CASE_SIZE
        return (x, y)


    def _drawGrid(self, window, color, lineWidth):
        for i in range(BoardParam.NUM_CASE):
            # vertical lines
            startPos = (
                self._boardBorderOrigin(window)[0] + i * BoardParam.CASE_SIZE - 1,
                self._boardBorderOrigin(window)[1] - 1
                )
            endPos = (
                self._boardBorderOrigin(window)[0] + i * BoardParam.CASE_SIZE - 1,
                self._boardBorderOrigin(window)[1] + BoardParam.BORDER_SIZE - 1
                )
            pg.draw.line(window.display, color, startPos, endPos, lineWidth)

            # horizontal lines
            startPos = (
                self._boardBorderOrigin(window)[0] - 1,
                self._boardBorderOrigin(window)[1] + i * BoardParam.CASE_SIZE - 1
                )
            endPos = (
                self._boardBorderOrigin(window)[0] + BoardParam.BORDER_SIZE - 1,
                self._boardBorderOrigin(window)[1] + i * BoardParam.CASE_SIZE - 1
                )
            pg.draw.line(window.display, color, startPos, endPos, lineWidth)


    def _drawStarPoints(self, window, color, circleRadius):
        starPoints = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
    
        for point in starPoints:
            center = (
                self._boardBorderOrigin(window)[0] + point[0] * BoardParam.CASE_SIZE,
                self._boardBorderOrigin(window)[1] + point[1] * BoardParam.CASE_SIZE
                )
            pg.draw.circle(window.display, color, center, circleRadius)


    def _drawPieces(self, window):
        self.boardState = window.game.boardState

        for row in range(BoardParam.NUM_CASE):
            for col in range(BoardParam.NUM_CASE):
                if self.boardState[row][col] != 0:
                    pos = self._getPosFromIndex(row, col, window)

                    player1Piece = window.themeManager.getPiecesImage(1)
                    player2Piece = window.themeManager.getPiecesImage(2)
                    pieceImage = player1Piece if self.boardState[row][col] == 1 else player2Piece

                    piecePos = Position.convert(pos, pieceImage.get_size(), PositionReference.CENTER)
                    window.display.blit(pieceImage, piecePos)


    def _drawHoverPiece(self, window):
        import math
        game = window.game
        hoverCell = game.hoverCell

        if game.proposedMove is not None:
            r, c = game.proposedMove
            if game.boardState[r][c] == 0:
                baseImage = window.themeManager.getPiecesImage(game.activePlayer)
                
                # Animate scale between 0.8 and 1.2
                scale = 1.0 + 0.2 * math.sin(pg.time.get_ticks() / 200.0)
                newSize = (int(baseImage.get_width() * scale), int(baseImage.get_height() * scale))
                
                hintImage = pg.transform.smoothscale(baseImage, newSize).convert_alpha()
                hintImage.set_alpha(self.hoverAlpha // 2) # More transparent
                
                pos = self._getPosFromIndex(r, c, window)
                piecePos = Position.convert(pos, hintImage.get_size(), PositionReference.CENTER)
                window.display.blit(hintImage, piecePos)

        if hoverCell is None:
            return

        # if player is AI don't show hover piece
        if game.mode is not None and game.mode.name == "PVE" and game.activePlayer == 2:
            return

        row, col = hoverCell
        if game.boardState[row][col] != 0:
            return

        if game._checkDoubleThree(row, col):
            from src.Game.assets import Assets
            orig = pg.image.load(Assets.CROSS).convert_alpha()
            refSize = window.themeManager.getPiecesImage(game.activePlayer).get_size()
            pieceImage = pg.transform.scale(orig, refSize)
        else:
            pieceImage = window.themeManager.getPiecesImage(game.activePlayer).copy()
            pieceImage.set_alpha(self.hoverAlpha)

        pos = self._getPosFromIndex(row, col, window)
        piecePos = Position.convert(pos, pieceImage.get_size(), PositionReference.CENTER)
        window.display.blit(pieceImage, piecePos)


    def draw(self, window):
        self.color = window.themeManager.getAccentColor()

        self._drawGrid(window, self.color, self.lineWidth)
        self._drawStarPoints(window, self.color, self.circleRadius)
        self._drawHoverPiece(window)
        self._drawPieces(window)
