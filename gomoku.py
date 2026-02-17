import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for _ in range(utils.BOARDSIZE)] for _ in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH
		self.pattern_dict_player1 = utils.create_pattern_dict(True)
		self.pattern_dict_player2 = utils.create_pattern_dict(False)


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
		if not self.isPositionOK(row, col):
			return 

		self.boardMap[row][col] = 1 if isPlayer1 else 2
		alignments = self.getAllDirectionsAlignments(row, col)
		self.boardMap[row][col] = 0

		score = 0
		pattern_dict_current = self.pattern_dict_player1 if isPlayer1 else self.pattern_dict_player2

		for alignment in alignments:
			for pattern, pattern_score in pattern_dict_current.items():
				if len(alignment) >= len(pattern):
					for i in range(len(alignment) - len(pattern) + 1):
						if tuple(alignment[i:i + len(pattern)]) == pattern:
							score += pattern_score

		return score

	def minimax(self, isPlayer1: bool, node, depth: int, maximizingPlayer: bool) -> int:
		if depth == 0: # or node is a terminal node then
			return self.evaluate(isPlayer1, 0, 0) # TODO: change 0, 0 to the last move

		if maximizingPlayer:
			value = float('-inf')
			# for each child of node do
			# 	value = max(value, minimax(child, depth - 1, False))
		else: # minimizing player
			value = float('inf')
			# for each child of node do
			# 	value = min(value, minimax(child, depth - 1, True))

		return value

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
