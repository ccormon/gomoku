from src.Game.Game import BoardParam
from src.AI.utils import Pattern, patterns_player1, patterns_player2


class GomokuAI:
	def __init__(self):
		self.size: int = BoardParam.NUM_CASE
		self.patterns: dict[int, list[Pattern]] = {
			1: patterns_player1,
			2: patterns_player2
		}


	def minimax(self):
		pass


	def findBestMove(self, game, player: int):
		board = game.boardState
