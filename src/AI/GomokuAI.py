import src.AI.utils as utils
from src.Game.Game import BoardParam


class GomokuAI():
	def __init__(self):
		self.boardMap = None
		self.pattern_dict_player1 = utils.create_pattern_dict(True)
		self.pattern_dict_player2 = utils.create_pattern_dict(False)
		self.numCase = BoardParam.NUM_CASE


	def getBoard(self):
		return self.boardMap


	def isInBoard(self, row: int, col: int):
		if row < 0 or row > self.numCase - 1 or col < 0 or col > self.numCase - 1:
			return False
		return True


	def isPositionOK(self, row: int, col: int):
		if not self.isInBoard(row, col):
			return False
		if self.boardMap[row][col] != 0:
			return False
		return True


	def doMove(self, isPlayer1: bool, row: int, col: int):
		if self.isPositionOK(row, col):
			self.boardMap[row][col] = 1 if isPlayer1 else 2


	def undoMove(self, row: int, col: int):
		if self.isInBoard(row, col):
			self.boardMap[row][col] = 0


	def getAllDirectionsAlignments(self, row: int, col: int) -> list:
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
		alignments = self.getAllDirectionsAlignments(row, col)

		score = 0
		pattern_dict_current = self.pattern_dict_player1 if isPlayer1 else self.pattern_dict_player2

		for alignment in alignments:
			for pattern, pattern_score in pattern_dict_current.items():
				if len(alignment) >= len(pattern):
					for i in range(len(alignment) - len(pattern) + 1):
						if tuple(alignment[i:i + len(pattern)]) == pattern:
							score += pattern_score

		return score


	# def getPossibleMoves(self) -> list[tuple[int, int]]:
	# 	moves = []

	# 	for row in range(self.numCase):
	# 		for col in range(self.numCase):
	# 			if self.boardMap[row][col] != 0:
	# 				for i in range(-1, 2):
	# 					for j in range(-1, 2):
	# 						if self.isPositionOK(row + i, col + j):
	# 							moves.append((row + i, col + j))

	# 	return moves


	def getPossibleMoves(self) -> list[tuple[int, int]]:
		moves = set()

		for row, col in self.playedMoves:
			for i in range(-1, 2):
				for j in range(-1, 2):
					r, c = row + i, col + j
					if self.isPositionOK(r, c):
						moves.add((r, c))

		return list(moves)


	def minimax(self, isPlayer1: bool, lastMove: tuple, depth: int, alpha: int, beta: int, maximizingPlayer: bool) -> int:
		if depth == 0:
			return self.evaluate(isPlayer1, lastMove[0], lastMove[1])

		if maximizingPlayer:
			value = float('-inf')
			for move in self.getPossibleMoves():
				self.doMove(isPlayer1, move[0], move[1])
				value = max(value, self.minimax(isPlayer1, move, depth - 1, alpha, beta, False))
				self.undoMove(move[0], move[1])
				if value >= beta:
					return value
				alpha = max(alpha, value)
		else:
			value = float('inf')
			for move in self.getPossibleMoves():
				self.doMove(not isPlayer1, move[0], move[1])
				value = min(value, self.minimax(isPlayer1, move, depth - 1, alpha, beta, True))
				self.undoMove(move[0], move[1])
				if alpha >= value:
					return value
				beta = min(beta, value)

		return value


	def findBestMove(self, game, isPlayer1: bool):
		self.boardMap = game.boardState
		bestMove = None
		bestValue = float('-inf')

		for move in self.getPossibleMoves():
			print(f"Testing move: {move}")
			self.doMove(isPlayer1, move[0], move[1])
			moveValue = self.minimax(isPlayer1, move, utils.DEPTH, float('-inf'), float('inf'), True)
			print(f"Move value: {moveValue}")
			self.undoMove(move[0], move[1])
			if moveValue > bestValue:
				bestValue = moveValue
				bestMove = move

		return bestMove


	# def drawBoard(self):
	# 	print("        ", end="")
	# 	for i in range(self.numCase):
	# 		if i < 10:
	# 			print(f"{i}   ", end="")
	# 		else:
	# 			print(f"{i}  ", end="")
	# 	print()
	# 	print()

	# 	for i in range(self.numCase):
	# 		for j in range(self.numCase):
	# 			if j == 0:
	# 				if i < 10:
	# 					print(f"{i}       ", end="")
	# 				else:
	# 					print(f"{i}      ", end="")
	# 			match self.boardMap[i][j]:
	# 				case 1:
	# 					state = 1
	# 				case 2:
	# 					state = 2
	# 				case _:
	# 					state = 0
	# 			print(f"{state}   ", end="")
	# 		print()
	# 	print()

# function minimax(node, depth, maximizingPlayer) is
# 	if depth = 0 or node is a terminal node then
# 		return the heuristic value of node
# 	if maximizingPlayer then
# 		value := −∞
# 		for each child of node do
# 			value := max(value, minimax(child, depth − 1, FALSE))
# 	else (* minimizing player *)
# 		value := +∞
# 		for each child of node do
# 			value := min(value, minimax(child, depth − 1, TRUE))
# 	return value
