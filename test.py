from gomokuAI import GomokuAI


def main():
	test_board = GomokuAI()
	test_board.placeAStone(True, 8, 3)
	test_board.placeAStone(False, 7, 2)
	test_board.drawBoardInTerminal()


if __name__ == "__main__":
	main()
