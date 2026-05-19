import random
from src.AI.utils import patterns_player1, patterns_player2


class GameState:
	def __init__(self, size: int):
		self.size = size
		self.grid = [[0 for _ in range(size)] for _ in range(size)]
		self.hash = 0
		self.score = 0

		random.seed(42)

		self.zobrist = [
			[
				[random.getrandbits(64) for _ in range(3)] for _ in range(size)
			] for _ in range(size)
		]


	def debug_state(self):														# <== A SUPPRIMER
		print("HASH:", self.hash)
		for row in self.grid:
			print(row)
		print("-----")


	def play(self, x, y, player):
		old_score = self.evaluate_lines_around(x, y)
		
		self.grid[x][y] = player
		self.hash ^= self.zobrist[x][y][player]
		
		new_score = self.evaluate_lines_around(x, y)
		
		self.score += (new_score - old_score)


	def undo(self, x, y):
		old_score = self.evaluate_lines_around(x, y)
		
		player = self.grid[x][y]
		self.hash ^= self.zobrist[x][y][player]
		self.grid[x][y] = 0
		
		new_score = self.evaluate_lines_around(x, y)
		
		self.score += (new_score - old_score)


	def get_lines_around(self, r: int, c: int) -> str:
		directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
		chars = []

		for dr, dc in directions:
			for i in range(-4, 5):
				nr = r + dr * i
				nc = c + dc * i

				if 0 <= nr < self.size and 0 <= nc < self.size:
					chars.append(str(self.grid[nr][nc]))
				else:
					chars.append('3')

			chars.append('#')

		return "".join(chars)


	def evaluate_lines_around(self, r: int, c: int) -> int:
		"""Evaluates the board state and returns a score from the perspective of player 1."""
		lines_str = self.get_lines_around(r, c)
		score = 0

		for pattern in patterns_player1:
			if pattern.pattern_str in lines_str:
				score += pattern.score * lines_str.count(pattern.pattern_str)

		for pattern in patterns_player2:
			if pattern.pattern_str in lines_str:
				score += pattern.score * lines_str.count(pattern.pattern_str)

		return score
