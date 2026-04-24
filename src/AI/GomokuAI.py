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


	def evaluateMove(self, state: GameState) -> int:
		"""Returns the global incremental score."""
		return state.score


	def getCandidateMoves(self, state: GameState) -> list[tuple[int, int]]:
		"""Returns a list of candidate moves (empty cells adjacent to occupied cells)."""
		size = self.size
		grid = state.grid

		pieces = [(r, c) for r in range(size) for c in range(size) if grid[r][c] != 0]

		if not pieces:
			return [(size // 2, size // 2)]

		moves = set()

		for r, c in pieces:
			for dr in range(-1, 2):
				for dc in range(-1, 2):
					nr, nc = r + dr, c + dc

					if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
						moves.add((nr, nc))

		return list(moves)


	def quickEvaluate(self, state: GameState, move: tuple[int, int], maximizingPlayer: bool) -> float:
		"""Quick heuristic evaluation for move ordering in minimax."""
		r, c = move
		player = 1 if maximizingPlayer else 2
		opponent = 2 if player == 1 else 1

		score = 0

		for dr in [-1, 0, 1]:
			for dc in [-1, 0, 1]:
				nr, nc = r + dr, c + dc

				if 0 <= nr < self.size and 0 <= nc < self.size:
					if state.grid[nr][nc] == player:
						score += 2
					elif state.grid[nr][nc] == opponent:
						score += 1

		return score


	def minimax(self, state: GameState, depth: int, alpha: float, beta: float, maximizingPlayer: bool) -> float:
		"""Minimax algorithm with alpha-beta pruning and transposition table."""
		if depth == 0:
			score = self.evaluateMove(state)
			return score

		moves = self.getCandidateMoves(state)
		moves = sorted(
			moves,
			key=lambda m: self.quickEvaluate(state, m, maximizingPlayer),
			reverse=True
		)

		if maximizingPlayer:
			max_eval = float('-inf')

			for (r, c) in moves:
				state.play(r, c, 1)
				evaluation = self.minimax(state, depth - 1, alpha, beta, False)
				state.undo(r, c)
				max_eval = max(max_eval, evaluation)
				alpha = max(alpha, evaluation)

				if beta <= alpha:
					break

			return max_eval

		else:
			min_eval = float('inf')

			for (r, c) in moves:
				state.play(r, c, 2)
				evaluation = self.minimax(state, depth - 1, alpha, beta, True)
				state.undo(r, c)
				min_eval = min(min_eval, evaluation)
				beta = min(beta, evaluation)

				if beta <= alpha:
					break

			return min_eval


	def findBestMove(self, state: GameState, player: int) -> tuple[int, int] | None:
		"""Finds the best move for the given player using the minimax algorithm."""
		state.debug_state()														# <== A SUPPRIMER

		best_move = None

		is_maximizing = (player == 1)
		best_score = float('-inf') if is_maximizing else float('inf')

		moves = self.getCandidateMoves(state)

		for (r, c) in moves:
			state.play(r, c, player)

			score = self.minimax(
				state, 
				depth=2, 
				alpha=float('-inf'), 
				beta=float('inf'), 
				maximizingPlayer=(not is_maximizing)
			)
			state.undo(r, c)

			if is_maximizing:
				if score > best_score:
					best_score = score
					best_move = (r, c)
			else:
				if score < best_score:
					best_score = score
					best_move = (r, c)

		print(f"Best move for player {player}: {best_move} with score {best_score}")		# <== A SUPPRIMER
		return best_move
