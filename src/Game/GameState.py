class GameState:
	def __init__(self, size: int):
		self.size = size
		self.grid = [[0 for _ in range(size)] for _ in range(size)]
		self.hash = 0


	def play(self, x: int, y: int, player: int):
		self.grid[x][y] = player


	def undo(self, x: int, y: int):
		self.grid[x][y] = 0
