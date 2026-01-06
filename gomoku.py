import utils


class Gomoku():
	def __init__(self):
		self.boardMap = [[0 for j in range(utils.BOARDSIZE)] for i in range(utils.BOARDSIZE)]
		self.depth = utils.DEPTH

	def get_boardMap(self):
		return self.boardMap

	def get_depth(self):
		return self.depth
