import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH


	def getBoard(self):
		return self.boardMap


	def placeAStone(self, isPlayer1, row, col):
		if self.isPositionOK(row, col):
			self.boardMap[row][col] = 1 if isPlayer1 else 2


	def isPositionOK(self, row, col):
		if row < 0 or row > 18 or col < 0 or row > 18:
			return False
		if self.boardMap[row][col] != 0:
			return False
		return True


	def evaluate(self, row, col):
		alignments = self.getAllDirectionsAlignments(row, col)


	def getAllDirectionsAlignments(self, row, col):
		directions = [[-1, 1], [0, 1], [1, 1], [1, 0]]
		alignments = []

		for direction in directions:
			alignment = []
			for i in range(5):
				tested_row = row + i * direction[0]
				tested_col = col + i * direction[1]
				if self.isPositionOK(tested_row, tested_col):
					alignment.append(self.boardMap[tested_row][tested_col])
			for i in range(5):
				tested_row = row - i * direction[0]
				tested_col = col - i * direction[1]
				if self.isPositionOK(tested_row, tested_col):
					alignment.append(self.boardMap[tested_row][tested_col])
			alignments.append(alignment)

		return alignments


	def isWinningConfiguration(self, alignment, isPlayer1):
		alignmentLen = alignment.size
		winConfLen = utils.PLAYER1_WINCONF[0].size

		if alignmentLen < winConfLen:
			return False

		winConf = utils.PLAYER1_WINCONF if isPlayer1 else utils.PLAYER2_WINCONF

		for conf in winConf:
			for i in range(alignmentLen - winConfLen + 1):
				if alignment[i:i + winConfLen] == conf:
					return True

		return False
