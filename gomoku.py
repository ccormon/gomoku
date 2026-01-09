import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH


	def getBoard(self):
		return self.boardMap


	def isPositionOK(self, row, col):
		if row < 0 or row > 18 or col < 0 or row > 18:
			return False
		if self.boardMap[row][col] != 0:
			return False
		return True


	def placeAStone(self, isAI, row, col):
		if self.isPositionOK(row, col):
			self.boardMap[row][col] = 1 if isAI else -1


	def evaluate(self, row, col):
		directions = [
			[-1, 1],
			[0, 1],
			[1, 1],
			[1, 0]
		]

		# for direction in directions:

