from dataclasses import dataclass


@dataclass(frozen=True)
class Pattern:
	pattern: tuple[int, ...]
	score: int

	@property
	def length(self):
		return len(self.pattern)


patterns_player1 = [
	Pattern((1, 1, 1, 1, 1), 2_000_000),
	Pattern((0, 1, 1, 1, 1, 0), 100_000),
	Pattern((1, 0, 1, 1, 1, 0), 50_000),
	Pattern((0, 1, 1, 1, 0, 1), 50_000),
	Pattern((0, 1, 1, 0, 1, 1, 0), 40_000),
	Pattern((2, 1, 1, 1, 0, 1), 10_000),
	Pattern((1, 0, 1, 1, 1, 2), 10_000),
	Pattern((2, 1, 1, 1, 1, 0), 10_000),
	Pattern((0, 1, 1, 1, 1, 2), 10_000),
	Pattern((0, 1, 1, 1, 0), 5_000),
	Pattern((0, 1, 0, 1, 1, 0), 3_000),
	Pattern((0, 1, 1, 0, 1, 0), 3_000),
	Pattern((2, 1, 1, 1, 0), 1_000),
	Pattern((0, 1, 1, 1, 2), 1_000),
	Pattern((2, 1, 1, 0, 1, 0), 500),
	Pattern((0, 1, 0, 1, 1, 2), 500),
	Pattern((0, 1, 1, 0), 300),
	Pattern((0, 1, 0, 1, 0), 300),
	Pattern((2, 1, 1, 0), 80),
	Pattern((0, 1, 1, 2), 80),
	Pattern((2, 1, 0, 1, 0), 40),
	Pattern((0, 1, 0, 1, 2), 40),
	Pattern((0, 1, 0), 20),
	Pattern((2, 1, 0), 10),
	Pattern((0, 1, 2), 10),
	Pattern((2, 1, 1, 2), 10),
	Pattern((2, 1, 1, 1, 2), 50),
	Pattern((2, 1, 1, 1, 1, 2), 100),
]


patterns_player2 = [
	Pattern((2, 2, 2, 2, 2), -2_000_000),
	Pattern((0, 2, 2, 2, 2, 0), -100_000),
	Pattern((2, 0, 2, 2, 2, 0), -50_000),
	Pattern((0, 2, 2, 2, 0, 2), -50_000),
	Pattern((0, 2, 2, 0, 2, 2, 0), -40_000),
	Pattern((1, 2, 2, 2, 0, 2), -10_000),
	Pattern((2, 0, 2, 2, 2, 1), -10_000),
	Pattern((1, 2, 2, 2, 2, 0), -10_000),
	Pattern((0, 2, 2, 2, 2, 1), -10_000),
	Pattern((0, 2, 2, 2, 0), -5_000),
	Pattern((0, 2, 0, 2, 2, 0), -3_000),
	Pattern((0, 2, 2, 0, 2, 0), -3_000),
	Pattern((1, 2, 2, 2, 0), -1_000),
	Pattern((0, 2, 2, 2, 1), -1_000),
	Pattern((1, 2, 2, 0, 2, 0), -500),
	Pattern((0, 2, 0, 2, 2, 1), -500),
	Pattern((0, 2, 2, 0), -300),
	Pattern((0, 2, 0, 2, 0), -300),
	Pattern((1, 2, 2, 0), -80),
	Pattern((0, 2, 2, 1), -80),
	Pattern((1, 2, 0, 2, 0), -40),
	Pattern((0, 2, 0, 2, 1), -40),
	Pattern((0, 2, 0), -20),
	Pattern((1, 2, 0), -10),
	Pattern((0, 2, 1), -10),
	Pattern((1, 2, 2, 1), -10),
	Pattern((1, 2, 2, 2, 1), -50),
	Pattern((1, 2, 2, 2, 2, 1), -100),
]
