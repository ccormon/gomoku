import utils
import argparse
from src.AI.GomokuAI import GomokuAI


def parse_args():
	parser = argparse.ArgumentParser(description="Play to Gomoku in your terminal.")
	parser.add_argument('-p', '--player', type=int, default=1, choices=[1, 2], help='Number of player (1 (default): against AI, 2 : with another player)')
	return parser.parse_args()


def drawBoardInTerminal(boardMap, nbPlayer):
	print("        ", end="")
	for i in range(utils.BOARDSIZE):
		if i < 10:
			print(f"{i}   ", end="")
		else:
			print(f"{i}  ", end="")
	print()
	print()

	for i in range(utils.BOARDSIZE):
		for j in range(utils.BOARDSIZE):
			if j == 0:
				if i < 10:
					print(f"{i}       ", end="")
				else:
					print(f"{i}      ", end="")
			match boardMap[i][j]:
				case 1:
					state = 1
				case 2:
					state = 2
				case _:
					state = 0
			print(f"{state}   ", end="")
		print()
	print()
	print(f"Player1: {1}")
	if nbPlayer == 1:
		print(f"AI:      {2}")
	else:
		print(f"Player2: {2}")


def play2Player():
	game = Gomoku()
	drawBoardInTerminal(Gomoku.getBoard(), 2)


def main():
	args = parse_args()
	if args.player == 2:
		play2Player()


if __name__ == "__main__":
	main()
