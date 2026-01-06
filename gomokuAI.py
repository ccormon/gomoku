import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH


	"""
	TEST FUNCTION TO REMOVE BEFORE SUBMIT
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
						state = utils.PLAYER
					case _:
						state = utils.EMPTY
				print(f"{state}   ", end="")
			print()
		print()
		print(f"Player: {utils.PLAYER}")
		print(f"AI:     {utils.AI}")


	def placeAStone(self, isAI, row, column):
		self.boardMap[row][column] = 1 if isAI else -1


	def
