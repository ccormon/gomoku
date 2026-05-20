import random
from src.AI.utils import patterns_player1, patterns_player2


class GameState:
	def __init__(self, size: int):
		self.size = size
		self.grid = [[0 for _ in range(size)] for _ in range(size)]
		self.hash = 0
		self.score = 0

		self.adj_counts = [[0 for _ in range(size)] for _ in range(size)]
		self.candidates = set()

		random.seed(42)

		self.zobrist = [
			[
				[random.getrandbits(64) for _ in range(3)] for _ in range(size)
			] for _ in range(size)
		]


	def debugState(self):														# <== A SUPPRIMER
		print("HASH:", self.hash)
		for row in self.grid:
			print(row)
		print("-----")


	def play(self, x: int, y: int, player: int):
		"""Places a piece for the given player at (x, y) and updates the game state."""
		old_score = self.evaluateLinesAround(x, y)

		self.grid[x][y] = player
		self.hash ^= self.zobrist[x][y][player]

		new_score = self.evaluateLinesAround(x, y)
		self.score += (new_score - old_score)

		if (x, y) in self.candidates:
			self.candidates.remove((x, y))

		for dx in range(-2, 3):
			for dy in range(-2, 3):
				if dx == 0 and dy == 0:
					continue
				nx, ny = x + dx, y + dy

				if 0 <= nx < self.size and 0 <= ny < self.size:
					self.adj_counts[nx][ny] += 1

					if self.grid[nx][ny] == 0 and self.adj_counts[nx][ny] == 1:
						self.candidates.add((nx, ny))


	def undo(self, x: int, y: int):
		"""Removes a piece from (x, y) and updates the game state accordingly."""
		old_score = self.evaluateLinesAround(x, y)

		player = self.grid[x][y]
		self.hash ^= self.zobrist[x][y][player]
		self.grid[x][y] = 0

		new_score = self.evaluateLinesAround(x, y)
		self.score += (new_score - old_score)

		for dx in range(-2, 3):
			for dy in range(-2, 3):
				if dx == 0 and dy == 0:
					continue
				nx, ny = x + dx, y + dy

				if 0 <= nx < self.size and 0 <= ny < self.size:
					self.adj_counts[nx][ny] -= 1

					if self.adj_counts[nx][ny] == 0 and (nx, ny) in self.candidates:
						self.candidates.remove((nx, ny))

		if self.adj_counts[x][y] > 0:
			self.candidates.add((x, y))


	def getLinesAround(self, r: int, c: int) -> str:
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


	def evaluateLinesAround(self, r: int, c: int) -> int:
		"""Evaluates the board state and returns a score from the perspective of player 1."""
		lines_str = self.getLinesAround(r, c)
		score = 0

		for pattern in patterns_player1:
			if pattern.pattern_str in lines_str:
				score += pattern.score * lines_str.count(pattern.pattern_str)

		for pattern in patterns_player2:
			if pattern.pattern_str in lines_str:
				score += pattern.score * lines_str.count(pattern.pattern_str)

		return score
