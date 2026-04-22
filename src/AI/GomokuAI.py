from src.Game.Game import BoardParam
from src.AI.utils import Pattern, patterns_player1, patterns_player2
from src.Game.GameState import GameState


class GomokuAI:
	def __init__(self):
		self.size: int = BoardParam.NUM_CASE
		self.patterns: dict[int, list[Pattern]] = {
			1: patterns_player1,
			2: patterns_player2
		}
		self.tt = {}


	def getLinesAround(self, grid: list[list[int]], r: int, c: int) -> list[list[int]]:
		directions = [(1,0), (0,1), (1,1), (1,-1)]
		lines = []

		for dr, dc in directions:
			line = []

			for i in range(-4, 5):
				nr = r + dr * i
				nc = c + dc * i

				if 0 <= nr < self.size and 0 <= nc < self.size:
					line.append(grid[nr][nc])
				else:
					line.append(3)  # bord (bloqué)

			lines.append(line)

		return lines


	def evaluateMove(self, state: GameState, r: int, c: int) -> int:
		"""Evaluates the board state and returns a score from the perspective of player 1."""
		grid = state.grid
		lines = self.getLinesAround(grid, r, c)

		score = 0

		for line in lines:
			for pattern in self.patterns[1]:
				for i in range(len(line) - pattern.length() + 1):
					if tuple(line[i:i + pattern.length()]) == pattern.pattern:
						score += pattern.score

			for pattern in self.patterns[2]:
				for i in range(len(line) - pattern.length() + 1):
					if tuple(line[i:i + pattern.length()]) == pattern.pattern:
						score += pattern.score

		return score


	def getCandidateMoves(self, state: GameState) -> list[tuple[int, int]]:
		"""Returns a list of candidate moves (empty cells adjacent to occupied cells)."""
		size = self.size
		grid = state.grid

		pieces = [(r, c) for r in range(size) for c in range(size) if grid[r][c] != 0]

		if not pieces:
			return [(size // 2, size // 2)]

		moves = set()

		for r, c in pieces:
			for dr in range(-2, 3):
				for dc in range(-2, 3):
					nr, nc = r + dr, c + dc

					if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
						moves.add((nr, nc))

		return list(moves)


	def quickEvaluate(self, state: GameState, move: tuple[int, int], maximizingPlayer: bool) -> float:
		"""Quick heuristic evaluation for move ordering in minimax."""
		r, c = move
		player = 1 if maximizingPlayer else 2

		state.play(r, c, player)
		score = self.evaluateMove(state, r, c)
		state.undo(r, c)

		return score


	def minimax(self, state: GameState, depth: int, alpha: float, beta: float, maximizingPlayer: bool, last_move: tuple[int, int]) -> float:
		"""Minimax algorithm with alpha-beta pruning and transposition table."""
		if state.hash in self.tt:
			stored_depth, stored_score = self.tt[state.hash]

			if stored_depth >= depth:
				return stored_score

		if depth == 0:
			score = self.evaluateMove(state, last_move[0], last_move[1])
			self.tt[state.hash] = (depth, score)
			return score

		moves = self.getCandidateMoves(state)
		moves = sorted(
			moves,
			key=lambda m: self.quickEvaluate(state, m, maximizingPlayer),
			reverse=maximizingPlayer
		)

		if maximizingPlayer:
			max_eval = float('-inf')

			for (r, c) in moves:
				state.play(r, c, 1)
				evaluation = self.minimax(state, depth - 1, alpha, beta, False, (r, c))
				state.undo(r, c)
				max_eval = max(max_eval, evaluation)
				alpha = max(alpha, evaluation)

				if beta <= alpha:
					break

			self.tt[state.hash] = (depth, max_eval)
			return max_eval

		else:
			min_eval = float('inf')

			for (r, c) in moves:
				state.play(r, c, 2)
				evaluation = self.minimax(state, depth - 1, alpha, beta, True, (r, c))
				state.undo(r, c)
				min_eval = min(min_eval, evaluation)
				beta = min(beta, evaluation)

				if beta <= alpha:
					break

			self.tt[state.hash] = (depth, min_eval)
			return min_eval


	def findBestMove(self, state: GameState, player: int) -> tuple[int, int] | None:
		"""Finds the best move for the given player using the minimax algorithm."""
		best_score = float('-inf')
		best_move = None

		moves = self.getCandidateMoves(state)

		for (r, c) in moves:
			state.play(r, c, player)
			score = self.minimax(state, depth=2, alpha=float('-inf'), beta=float('inf'), maximizingPlayer=False, last_move=(r, c))
			state.undo(r, c)

			if score > best_score:
				best_score = score
				best_move = (r, c)

		return best_move
