import random


class GameState:
	def __init__(self, size: int):
		self.size = size
		self.grid = [[0 for _ in range(size)] for _ in range(size)]
		self.hash = 0

		random.seed(42)

		self.zobrist = [
			[
				[random.getrandbits(64) for _ in range(3)] for _ in range(size)
			] for _ in range(size)
		]


	def debug_state(self):
		print("HASH:", self.hash)
		for row in self.grid:
			print(row)
		print("-----")


	def play(self, x, y, player):
		self.grid[x][y] = player
		self.hash ^= self.zobrist[x][y][player]


	def undo(self, x, y):
		player = self.grid[x][y]
		self.hash ^= self.zobrist[x][y][player]
		self.grid[x][y] = 0
