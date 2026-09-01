import time
import unittest

from src.AI.GomokuAI import GomokuAI
from src.Game.GameState import GameState


class PerformanceTests(unittest.TestCase):
    def test_representative_search_budget(self):
        ai = GomokuAI()
        try:
            state = GameState(19)
            for row, col, player in [
                (9, 9, 1), (9, 10, 2), (10, 10, 1), (8, 8, 2),
                (10, 9, 1), (8, 9, 2), (11, 9, 1), (7, 9, 2),
            ]:
                state.play(row, col, player)
            started = time.perf_counter()
            move = ai.findBestMove(state, 1, {1: 0, 2: 0}, budget_ms=450)
            elapsed = time.perf_counter() - started
            self.assertIsNotNone(move)
            self.assertLessEqual(ai.last_search.elapsed_seconds, 0.475)
            self.assertLessEqual(elapsed, 0.525)
            self.assertGreaterEqual(ai.last_search.completed_depth, 10)
        finally:
            ai.close()


if __name__ == "__main__":
    unittest.main()
