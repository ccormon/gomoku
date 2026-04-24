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


	def evaluate_lines_around(self, r: int, c: int) -> int:
		"""Evaluates the board state and returns a score from the perspective of player 1."""
		lines = self.get_lines_around(r, c)
		score = 0

		for line in lines:
			for pattern in patterns_player1:
				for i in range(len(line) - pattern.length() + 1):
					if tuple(line[i:i + pattern.length()]) == pattern.pattern:
						score += pattern.score

			for pattern in patterns_player2:
				for i in range(len(line) - pattern.length() + 1):
					if tuple(line[i:i + pattern.length()]) == pattern.pattern:
						score += pattern.score

		return score


	def get_lines_around(self, r: int, c: int) -> list[list[int]]:
		directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
		lines = []

		for dr, dc in directions:
			line = []
			for i in range(-4, 5):
				nr = r + dr * i
				nc = c + dc * i

				if 0 <= nr < self.size and 0 <= nc < self.size:
					line.append(self.grid[nr][nc])
				else:
					line.append(3)

			lines.append(line)

		return lines
