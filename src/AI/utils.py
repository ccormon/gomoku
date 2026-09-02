class Pattern:
    def __init__(self, pattern: tuple[int, ...], score: int):
        self.pattern = pattern
        self.score = score
        self.pattern_str = "".join(map(str, pattern))

    def length(self):
        return len(self.pattern)


# Kept for GameState compatibility. The AI evaluation now lives in C++.
patterns_player1 = []
patterns_player2 = []
patterns_freethree_player1 = []
patterns_freethree_player2 = []
