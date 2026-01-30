import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH


	def getBoard(self):
		return self.boardMap


	def placeAStone(self, isPlayer1: bool, row: int, col: int):
		if self.isPositionOK(row, col):
			self.boardMap[row][col] = 1 if isPlayer1 else 2


	def isInBoard(self, row: int, col: int):
		if row < 0 or row > 18 or col < 0 or row > 18:
			return False
		return True


	def isPositionOK(self, row: int, col: int):
		if not self.isInBoard(row, col):
			return False
		if self.boardMap[row][col] != 0:
			return False
		return True


	def getAllDirectionsAlignments(self, row: int, col: int):
		directions = [[-1, 1], [0, 1], [1, 1], [1, 0]]
		alignments = []

		for direction in directions:
			alignment = []
			alignment.append(self.boardMap[row][col])
			for i in range(5):
				tested_row = row + i * direction[0]
				tested_col = col + i * direction[1]
				if (not (tested_row == row and tested_col == col)
					and self.isInBoard(tested_row, tested_col)):
					alignment.append(self.boardMap[tested_row][tested_col])
			for i in range(5):
				tested_row = row - i * direction[0]
				tested_col = col - i * direction[1]
				if (not (tested_row == row and tested_col == col)
					and self.isInBoard(tested_row, tested_col)):
					alignment.insert(0, self.boardMap[tested_row][tested_col])
			alignments.append(alignment)

		return alignments


	def evaluate(self, isPlayer1: bool, row: int, col: int):
		if not self.isPositionOK(row, col):
			return 
		self.boardMap[row][col] = 1 if isPlayer1 else 2
		alignments = self.getAllDirectionsAlignments(row, col)
		print(alignments)
		self.boardMap[row][col] = 0
