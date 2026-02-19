BOARDSIZE = 10
DEPTH = 3


PLAYER1 = 'X'
PLAYER2 = 'O'
EMPTY = '·'


def create_pattern_dict(isPlayer1: bool) -> dict:
	EMPTY = 0
	pattern_dict = {}

	for player in (1, 2):
		opponent = 2 if player == 1 else 1
		if isPlayer1:
			sign = 1 if player == 1 else -1
		else:
			sign = -1 if player == 1 else 1

		pattern_dict[(player, player, player, player, player)] = 1_000_000 * sign

		pattern_dict[(EMPTY, player, player, player, player, EMPTY)] = 100_000 * sign
		pattern_dict[(EMPTY, player, player, player, EMPTY, player, EMPTY)] = 10_000 * sign
		pattern_dict[(EMPTY, player, EMPTY, player, player, player, EMPTY)] = 10_000 * sign
		pattern_dict[(EMPTY, player, player, EMPTY, player, player, EMPTY)] = 10_000 * sign

		pattern_dict[(opponent, player, player, player, player, opponent)] = -10 * sign

		pattern_dict[(EMPTY, player, player, player, EMPTY)] = 1_000 * sign
		pattern_dict[(EMPTY, player, EMPTY, player, player, EMPTY)] = 1_000 * sign
		pattern_dict[(EMPTY, player, player, EMPTY, player, EMPTY)] = 1_000 * sign

		pattern_dict[(opponent, player, player, player, opponent)] = -10 * sign

		pattern_dict[(EMPTY, EMPTY, player, player, EMPTY)] = 100 * sign
		pattern_dict[(EMPTY, player, player, EMPTY, EMPTY)] = 100 * sign
		pattern_dict[(EMPTY, player, EMPTY, player, EMPTY)] = 100 * sign

	return pattern_dict
