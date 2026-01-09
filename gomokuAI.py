import utils


class GomokuAI():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH


	"""
	TEST FUNCTION
	"""
	def drawBoardInTerminal(self):
		print("        ", end="")
		for i in range(utils.BOARDSIZE):
			if i < 10:
				print(f"{i}   ", end="")
			else:
				print(f"{i}  ", end="")
		print()
		print()

		for i in range(utils.BOARDSIZE):
			for j in range(utils.BOARDSIZE):
				if j == 0:
					if i < 10:
						print(f"{i}       ", end="")
					else:
						print(f"{i}      ", end="")
				match self.boardMap[i][j]:
					case 1:
						state = utils.AI
					case -1:
						state = utils.PLAYER1
					case _:
						state = utils.EMPTY
				print(f"{state}   ", end="")
			print()
		print()
		print(f"Player: {utils.PLAYER1}")
		print(f"AI:     {utils.AI}")


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

