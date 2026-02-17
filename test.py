from gomoku import Gomoku
from gomokuCLI import *
from utils import *


def main():
	test_board = Gomoku()
	test_board.placeAStone(True, 8, 3)
	test_board.placeAStone(True, 9, 3)
	test_board.placeAStone(True, 10, 3)
	test_board.placeAStone(False, 7, 2)
	drawBoardInTerminal(test_board.getBoard(), 1)
	print()
	print(test_board.evaluate(True, 7, 3))



if __name__ == "__main__":
	main()
