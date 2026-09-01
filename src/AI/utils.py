class Pattern:
    def __init__(self, pattern: tuple[int, ...], score: int):
        self.pattern = pattern
        self.score = score
        self.pattern_str = "".join(map(str, pattern))

    def length(self):
        return len(self.pattern)


# Conservés pour la compatibilité de GameState. L'évaluation utilisée par l'IA
# vit désormais dans le moteur C++.
patterns_player1 = []
patterns_player2 = []
patterns_freethree_player1 = []
patterns_freethree_player2 = []
