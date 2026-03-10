from GomokuAI import GomokuAI
from gomokuCLI import *
from utils import *


def main():
	test_board = Gomoku()
	test_board.doMove(True, 5, 3)
	test_board.doMove(True, 6, 3)
	test_board.doMove(True, 7, 3)
	test_board.doMove(False, 4, 2)
	drawBoardInTerminal(test_board.getBoard(), 1)
	print()
	print(test_board.findBestMove(True))



if __name__ == "__main__":
	main()
