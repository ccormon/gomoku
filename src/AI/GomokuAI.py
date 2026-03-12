from typing import List, Tuple, Set
from src.Game.Game import BoardParam
from src.AI.utils import DEPTH


Board = List[List[int]]
Move = Tuple[int, int]
StoneSet = Set[Move]


class GomokuAI:
	def __init__(self) -> None:
		self.size: int = BoardParam.NUM_CASE


	# -------------------------
	# UTILITIES
	# -------------------------

	def isInBoard(self, row: int, col: int) -> bool:
		"""Check if the given position is within the board boundaries."""
		return 0 <= row < self.size and 0 <= col < self.size


	def isEmpty(self, board: Board, row: int, col: int) -> bool:
		"""Check if the given position is empty."""
		return self.isInBoard(row=row, col=col) and board[row][col] == 0


	# -------------------------
	# MOVE GENERATION
	# -------------------------

	def getPossibleMoves(self, board: Board, stones: StoneSet) -> List[Move]:
		"""Generate a list of possible moves based on the current board state and existing stones."""
		if not stones:
			mid: int = self.size // 2
			return [(mid, mid)]

		moves: Set[Move] = set()

		for row, col in stones:
			for dr in range(-1, 2):
				for dc in range(-1, 2):

					r: int = row + dr
					c: int = col + dc

					if self.isEmpty(board=board, row=r, col=c):
						moves.add((r, c))

		return list(moves)


	# -------------------------
	# ALIGNMENTS
	# -------------------------

	def getAlignments(self, board: Board, row: int, col: int) -> List[str]:
		"""Get the alignments (lines) of pieces in all four directions (horizontal, vertical, diagonal) for the given position."""
		directions: List[Tuple[int, int]] = [
			(1, 0),
			(0, 1),
			(1, 1),
			(1, -1)
		]
		alignments: List[str] = []

		for dr, dc in directions:
			line: List[str] = []

			for i in range(-4, 5):
				r: int = row + dr * i
				c: int = col + dc * i

				if self.isInBoard(r, c):
					line.append(str(board[r][c]))

			alignments.append(''.join(line))

		return alignments


	# -------------------------
	# POSITION EVALUATION
	# -------------------------

	def evaluatePosition(self, board: Board, row: int, col: int, player: int) -> int:
		"""Evaluate the given position for the specified player based on potential alignments and patterns."""
		opponent: int = 2 if player == 1 else 1
		patterns: dict[str, int] = {
			'11111': 100000,
			'011110': 10000,
			'01110': 1000,
			'0110': 100,
		}
		score: int = 0
		alignments: List[str] = self.getAlignments(board=board, row=row, col=col)

		for line in alignments:
			for pattern, value in patterns.items():
				playerPattern: str = pattern.replace('1', str(player))
				opponentPattern: str = pattern.replace('1', str(opponent))

				score += line.count(playerPattern) * value
				score -= line.count(opponentPattern) * value

		return score


	def evaluateBoard(self, board: Board, stones: StoneSet, player: int) -> int:
		"""Evaluate the entire board for the specified player by summing the scores of all positions occupied by their pieces."""
		total: int = 0

		for r, c in stones:
			total += self.evaluatePosition(board=board, row=r, col=c, player=player)

		return total


	# -------------------------
	# MINIMAX
	# -------------------------

	def minimax(self, board: Board, stones: StoneSet, depth: int, alpha: float, beta: float, player: int, maximizing: bool) -> int:
		"""Minimax algorithm with alpha-beta pruning to evaluate the best move for the specified player."""
		if depth == 0:
			return self.evaluateBoard(board=board, stones=stones, player=player)

		moves: List[Move] = self.getPossibleMoves(board=board, stones=stones)

		if maximizing:
			best: float = float('-inf')

			for r, c in moves:
				board[r][c] = player
				stones.add((r, c))

				value: int = self.minimax(board=board, stones=stones, depth=depth - 1, alpha=alpha, beta=beta, player=player, maximizing=False)

				board[r][c] = 0
				stones.discard((r, c))

				best = max(best, value)
				alpha = max(alpha, value)

				if beta <= alpha:
					break

			return int(best)

		else:
			opponent: int = 2 if player == 1 else 1
			best: float = float('inf')

			for r, c in moves:
				board[r][c] = opponent
				stones.add((r, c))

				value: int = self.minimax(board=board, stones=stones, depth=depth - 1, alpha=alpha, beta=beta, player=player, maximizing=True)

				board[r][c] = 0
				stones.discard((r, c))

				best = min(best, value)
				beta = min(beta, value)

				if beta <= alpha:
					break

			return int(best)


	# -------------------------
	# BEST MOVE
	# -------------------------

	def findBestMove(self, game, player: int, depth: int = DEPTH) -> Move | None:
		"""Find the best move for the specified player using the minimax algorithm."""
		board: Board = game.boardState
		stones: StoneSet = set(game.stonesLocations)

		moves: List[Move] = self.getPossibleMoves(board=board, stones=stones)

		bestMove: Move | None = None
		bestScore: float = float('-inf')

		for r, c in moves:
			board[r][c] = player
			stones.add((r, c))

			score: int = self.minimax(board=board, stones=stones, depth=depth - 1, alpha=float('-inf'), beta=float('inf'), player=player, maximizing=False)

			board[r][c] = 0
			stones.discard((r, c))

			if score > bestScore:
				bestScore = score
				bestMove = (r, c)

		return bestMove
