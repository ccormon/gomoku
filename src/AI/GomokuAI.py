import src.AI.utils as utils
from src.Game.Game import BoardParam


class GomokuAI():
	def __init__(self):
		self.numCase = BoardParam.NUM_CASE

		self.boardMap = None
		self.stonesLocations = set()
		self.candidateMoves = set()

		self.scorePlayer1 = {}
		self.scorePlayer2 = {}

		self.patternDictPlayer1 = utils.create_pattern_dict(isPlayer1=True)
		self.patternDictPlayer2 = utils.create_pattern_dict(isPlayer1=False)


	def create_pattern_dict(isPlayer1: bool) -> dict:
		EMPTY = "0"
		pattern_dict = {}

		for player in ("1", "2"):
			opponent = "2" if player == "1" else "1"

			sign = 1 if (player == "1") == isPlayer1 else -1
			# if isPlayer1:
			# 	sign = 1 if player == "1" else -1
			# else:
			# 	sign = -1 if player == "1" else 1

			def add(pattern, score):
				pattern_dict["".join(pattern)] = score * sign

			add((player, player, player, player, player), 1_000_000)
			add((EMPTY, player, player, player, player, EMPTY), 100_000)
			add((EMPTY, player, player, player, EMPTY, player, EMPTY), 10_000)
			add((EMPTY, player, EMPTY, player, player, player, EMPTY), 10_000)
			add((EMPTY, player, player, EMPTY, player, player, EMPTY), 10_000)
			add((opponent, player, player, player, player, opponent), -10)
			add((EMPTY, player, player, player, EMPTY), 1_000)
			add((EMPTY, player, EMPTY, player, player, EMPTY), 1_000)
			add((EMPTY, player, player, EMPTY, player, EMPTY), 1_000)
			add((opponent, player, player, player, opponent), -10)
			add((EMPTY, EMPTY, player, player, EMPTY), 100)
			add((EMPTY, player, player, EMPTY, EMPTY), 100)
			add((EMPTY, player, EMPTY, player, EMPTY), 100)

		return pattern_dict


	def getBoard(self):
		return self.boardMap


	def isInBoard(self, row: int, col: int) -> bool:
		return 0 <= row < self.numCase and 0 <= col < self.numCase


	def isPositionOK(self, row: int, col: int) -> bool:
		return self.isInBoard(row, col) and self.boardMap[row][col] == 0


	def updateCandidateMoves(self, row: int, col: int, add=True):
		for dr in range(-1, 2):
			for dc in range(-1, 2):
				r, c = row + dr, col + dc
				if self.isPositionOK(r, c):
					if add:
						self.candidateMoves.add((r, c))
					else:
						self.candidateMoves.discard((r, c))


	def updateScore(self, isPlayer1: bool, row: int, col: int, add=True):
		patterns = self.pattern_dict_player1 if isPlayer1 else self.pattern_dict_player2
		scores = self.scores_player1 if isPlayer1 else self.scores_player2
		directions = [(-1, 1), (0, 1), (1, 1), (1, 0)]

		for d, (dr, dc) in enumerate(directions):
			for i in range(-4, 5):
				r = row + i * dr
				c = col + i * dc

				if not self.isInBoard(r, c):
					continue

				# construire alignment
				alignment = []

				for j in range(-4, 5):
					rr = r + j * dr
					cc = c + j * dc

					if self.isInBoard(rr, cc):
						alignment.append(str(self.boardMap[rr][cc]))

				s = "".join(alignment)
				val = 0

				for pattern, _ in patterns.items():
					val += s.count(pattern)

				key = (r, c, d)

				if add:
					scores[key] = val
				else:
					scores.pop(key, None)


	def doMove(self, isPlayer1: bool, row: int, col: int):
		self.boardMap[row][col] = 1 if isPlayer1 else 2
		self.stones.add((row, col))
		self.updateCandidateMoves(row, col, add=True)
		self.updateScore(isPlayer1, row, col, add=True)


	def undoMove(self, row: int, col: int):
		if self.isInBoard(row, col):
			self.boardMap[row][col] = 0


	def getAllDirectionsAlignments(self, row: int, col: int) -> str:
		board = self.boardMap
		size = self.numCase

		directions = [(-1, 1), (0, 1), (1, 1), (1, 0)]
		alignments = []

		for dr, dc in directions:
			chars = []

			for i in range(-4, 5):
				r = row + i * dr
				c = col + i * dc

				if 0 <= r < size and 0 <= c < size:
					chars.append(str(board[r][c]))

			alignments.append("".join(chars))

		return alignments


	def evaluate(self, isPlayer1: bool, row: int, col: int) -> int:
		patterns = self.patternDictPlayer1 if isPlayer1 else self.patternDictPlayer2
		alignments = self.getAllDirectionsAlignments(row, col)

		score = 0
		items = patterns.items()

		for alignment in alignments:
			for pattern, pattern_score in items:
				n = alignment.count(pattern)
				if n:
					score += n * pattern_score

		return score


	def getPossibleMoves(self) -> list[tuple[int, int]]:
		moves = set()
		directions = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1),  (0, 0),  (0, 1),
			(1, -1),  (1, 0),  (1, 1)
		]

		for row, col in self.stonesLocations:
			for i, j in directions:
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
		self.stonesLocations = game.stonesLocations

		bestMove = None
		bestValue = float('-inf')
		moves = self.getPossibleMoves()

		moves.sort(
			key=lambda m: self.evaluate(isPlayer1, m[0], m[1]),
			reverse=True
		)

		for row, col in moves:
			self.doMove(isPlayer1, row, col)

			value = self.minimax(
				isPlayer1,
				(row, col),
				utils.DEPTH,
				float('-inf'),
				float('inf'),
				True
			)

			self.undoMove(row, col)

			if value > bestValue:
				bestValue = value
				bestMove = (row, col)

			if bestValue >= utils.WIN_SCORE:
				break

		return bestMove
