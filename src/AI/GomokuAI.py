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
		self.transposition_table = {}
		self.killer_moves: list[list[tuple[int, int] | None]] = [[None, None] for _ in range(30)]
		self.history_table = [[[0.0 for _ in range(3)] for _ in range(self.size)] for _ in range(self.size)]


	def evaluateMove(self, state: GameState) -> int:
		"""Returns the global incremental score."""
		return state.score


	def getCandidateMoves(self, state: GameState) -> list[tuple[int, int]]:
		"""Returns a list of candidate moves (empty cells adjacent to occupied cells)."""
		if not state.candidates:
			return [(self.size // 2, self.size // 2)]

		return list(state.candidates)


	def quickEvaluate(self, state: GameState, move: tuple[int, int], maximizingPlayer: bool) -> float:
		"""Heuristic evaluation for move ordering in minimax (Beam Search aware)."""
		r, c = move
		player = 1 if maximizingPlayer else 2
		
		state.grid[r][c] = player
		score_player = state.evaluateLinesAround(r, c)
		state.grid[r][c] = 0
		
		opponent = 2 if player == 1 else 1
		state.grid[r][c] = opponent
		score_opponent = state.evaluateLinesAround(r, c)
		state.grid[r][c] = 0

		return abs(score_player) + 2 *abs(score_opponent)


	def minimax(self, state: GameState, depth: int, alpha: float, beta: float, maximizingPlayer: bool) -> float:
		"""Minimax algorithm with alpha-beta pruning and transposition table."""
		alpha_original = alpha
		beta_original = beta

		if state.hash in self.transposition_table:
			entry = self.transposition_table[state.hash]
			if entry['depth'] >= depth:
				if entry['flag'] == 'EXACT':
					return entry['value']
				elif entry['flag'] == 'LOWERBOUND':
					alpha = max(alpha, entry['value'])
				elif entry['flag'] == 'UPPERBOUND':
					beta = min(beta, entry['value'])

				if alpha >= beta:
					return entry['value']

		if depth == 0 or abs(state.score) >= 1_000_000:
			score = self.evaluateMove(state)
			if abs(score) >= 1_000_000:
				score += (depth * 1000) if score > 0 else -(depth * 1000)
			return score

		moves = self.getCandidateMoves(state)

		def move_score(move):
			r, c = move
			# score = self.quickEvaluate(state, move, maximizingPlayer)
			quick_score = self.quickEvaluate(state, move, maximizingPlayer)
			history_score = self.history_table[r][c][1 if maximizingPlayer else 2]

			if move == self.killer_moves[depth][0]:
				history_score += 1_000_000
			elif move == self.killer_moves[depth][1]:
				history_score += 500_000

			return quick_score + history_score

		moves = sorted(moves, key=move_score, reverse=True)
		moves = moves[:10]

		if maximizingPlayer:
			max_eval = float('-inf')

			for (r, c) in moves:
				state.play(r, c, 1)
				evaluation = self.minimax(state, depth - 1, alpha, beta, False)
				state.undo(r, c)
				max_eval = max(max_eval, evaluation)
				alpha = max(alpha, evaluation)

				if beta <= alpha:
					self.history_table[r][c][1] += depth * depth
					if self.killer_moves[depth][0] != (r, c):
						self.killer_moves[depth][1] = self.killer_moves[depth][0]
						self.killer_moves[depth][0] = (r, c)
					break

			best_eval = max_eval

		else:
			min_eval = float('inf')

			for (r, c) in moves:
				state.play(r, c, 2)
				evaluation = self.minimax(state, depth - 1, alpha, beta, True)
				state.undo(r, c)
				min_eval = min(min_eval, evaluation)
				beta = min(beta, evaluation)

				if beta <= alpha:
					self.history_table[r][c][2] += depth * depth
					if self.killer_moves[depth][0] != (r, c):
						self.killer_moves[depth][1] = self.killer_moves[depth][0]
						self.killer_moves[depth][0] = (r, c)
					break

			best_eval = min_eval

		flag = 'EXACT'
		if best_eval <= alpha_original:
			flag = 'UPPERBOUND'
		elif best_eval >= beta_original:
			flag = 'LOWERBOUND'

		self.transposition_table[state.hash] = {
			'value': best_eval,
			'depth': depth,
			'flag': flag
		}

		return best_eval


	def findBestMove(self, state: GameState, player: int) -> tuple[int, int] | None:
		"""Finds the best move for the given player using the minimax algorithm."""
		state.debugState()														# <== A SUPPRIMER

		# self.history_table = [[[0.0 for _ in range(3)] for _ in range(self.size)] for _ in range(self.size)]

		best_move = None

		is_maximizing = (player == 1)
		best_score = float('-inf') if is_maximizing else float('inf')

		moves = self.getCandidateMoves(state)

		for (r, c) in moves:
			state.play(r, c, player)

			score = self.minimax(
				state, 
				depth=4, 
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

		print(f"Best move for player {player}: {best_move} with score {best_score}\n")		# <== A SUPPRIMER

		return best_move
