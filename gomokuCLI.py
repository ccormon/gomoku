import utils
import argparse


def parse_args():
	parser = argparse.ArgumentParser(description="Play to Gomoku in your terminal.")
	parser.add_argument('-p', '--player', type=int, default=1, choices=[1, 2], help='Number of player (1 (default): against AI, 2 : with another player)')
	return parser.parse_args()


def drawBoardInTerminal(boardMap):
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
					state = utils.AI
				case -1:
					state = utils.PLAYER1
				case _:
					state = utils.EMPTY
			print(f"{state}   ", end="")
		print()
	print()
	print(f"Player: {utils.PLAYER1}")
	print(f"AI:     {utils.AI}")


def main():
	args = parse_args()
	if args.player == 1:
		print('You play against AI')
	elif args.player == 2:
		print('You play against the dummy next to you (be careful)')
	else:
		print('wtf')


if __name__ == "__main__":
	main()
