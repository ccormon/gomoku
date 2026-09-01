import ctypes
import unittest

from src.AI.GomokuAI import GomokuAI
from src.Game.Game import Game, GameMode
from src.Game.GameState import GameState


class NativeBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ai = GomokuAI()

    @classmethod
    def tearDownClass(cls):
        cls.ai.close()

    def test_empty_board_returns_center_and_metrics(self):
        state = GameState(19)
        self.assertEqual(self.ai.findBestMove(state, 1, {1: 0, 2: 0}), (9, 9))
        self.assertEqual(self.ai.last_search.completed_depth, 0)
        self.assertLessEqual(self.ai.last_search.elapsed_seconds, 0.5)

    def test_input_board_is_not_modified(self):
        state = GameState(19)
        state.play(9, 9, 1)
        before = [row[:] for row in state.grid]
        move = self.ai.findBestMove(state, 2, {1: 0, 2: 0})
        self.assertEqual(state.grid, before)
        self.assertEqual(state.grid[move[0]][move[1]], 0)

    def test_invalid_player_is_rejected(self):
        with self.assertRaises(ValueError):
            self.ai.findBestMove(GameState(19), 3)


class PythonRuleParityTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.gomokuAI.close()

    def test_double_three_is_forbidden(self):
        for row, col in [(9, 8), (9, 10), (8, 9), (10, 9)]:
            self.game.state.grid[row][col] = 1
        self.assertTrue(self.game._checkDoubleThreeForPlayer(9, 9, 1))

    def test_capture_allows_double_three(self):
        for row, col in [(8, 9), (10, 9), (8, 8), (10, 10), (9, 12)]:
            self.game.state.grid[row][col] = 1
        self.game.state.grid[9][10] = 2
        self.game.state.grid[9][11] = 2
        self.assertFalse(self.game._checkDoubleThreeForPlayer(9, 9, 1))

    def test_breakable_five_is_not_an_immediate_win(self):
        for col in range(5, 10):
            self.game.state.grid[9][col] = 1
        self.game.state.grid[10][7] = 1
        self.game.state.grid[8][7] = 2
        self.assertTrue(self.game._canBreakAlignmentOrWinByCapture(1))

    def test_front_metrics_use_real_ai_search_average(self):
        self.game.init(GameMode.PVE)
        self.game.timerHistory = [(1, 2.0), (2, 8.0), (1, 4.0), (2, 9.0)]
        self.game.aiTimerHistory = [0.2, 0.4]
        self.assertAlmostEqual(self.game.averageMoveTime(1), 3.0)
        self.assertAlmostEqual(self.game.averageMoveTime(2), 0.3)

    def test_turn_and_last_move_front_properties(self):
        self.game.init(GameMode.PVP)
        self.assertEqual(self.game.turnNumber, 0)
        self.assertIsNone(self.game.lastMove)
        self.game.moveHistory.append((1, 9, 9))
        self.assertEqual(self.game.turnNumber, 0)
        self.assertEqual(self.game.lastMove, (9, 9))
        self.game.moveHistory.append((2, 9, 10))
        self.assertEqual(self.game.turnNumber, 1)


if __name__ == "__main__":
    unittest.main()
