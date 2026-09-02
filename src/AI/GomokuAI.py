from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from threading import Lock


class _NativeSearchResult(ctypes.Structure):
    _fields_ = [
        ("row", ctypes.c_int),
        ("col", ctypes.c_int),
        ("score", ctypes.c_int),
        ("completed_depth", ctypes.c_int),
        ("nodes", ctypes.c_uint64),
        ("elapsed_us", ctypes.c_uint64),
        ("status", ctypes.c_int),
    ]


@dataclass(frozen=True)
class SearchMetrics:
    """Metrics reported by the native engine for its latest search."""

    score: int = 0
    completed_depth: int = 0
    nodes: int = 0
    elapsed_seconds: float = 0.0
    status: int = 0


class GomokuAI:
    """Thread-safe Python wrapper around the native Gomoku engine."""

    BOARD_SIZE = 19
    DEFAULT_BUDGET_MS = 450

    def __init__(self, library_path: str | Path | None = None):
        """Load the native library and create one reusable engine instance."""

        project_root = Path(__file__).resolve().parents[2]
        path = Path(library_path) if library_path else project_root / "build" / "libgomoku_ai.so"
        if not path.exists():
            raise RuntimeError(f"Moteur IA introuvable: {path}. Lancez `make`.")

        self._library = ctypes.CDLL(str(path))
        self._configure_signatures()
        self._engine = self._library.gomoku_engine_create()
        if not self._engine:
            raise MemoryError("Impossible de créer le moteur Gomoku")
        self._lock = Lock()
        self.last_search = SearchMetrics()

    def _configure_signatures(self):
        """Declare the native C signatures used by ctypes."""

        self._library.gomoku_engine_create.argtypes = []
        self._library.gomoku_engine_create.restype = ctypes.c_void_p
        self._library.gomoku_engine_destroy.argtypes = [ctypes.c_void_p]
        self._library.gomoku_engine_destroy.restype = None
        self._library.gomoku_find_best_move.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(_NativeSearchResult),
        ]
        self._library.gomoku_find_best_move.restype = ctypes.c_int

    def close(self):
        """Release the native engine; repeated calls are safe."""

        engine = getattr(self, "_engine", None)
        if engine:
            self._library.gomoku_engine_destroy(engine)
            self._engine = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def findBestMove(self, state, player: int, captures=None, budget_ms: int = DEFAULT_BUDGET_MS):
        """Return the best legal ``(row, column)`` move for ``player``.

        Args:
            state: Object exposing a 19 x 19 ``grid`` of values 0, 1, and 2.
            player: Player to move, either 1 or 2.
            captures: Mapping of player numbers to captured-stone counts.
            budget_ms: Maximum native search time in milliseconds.

        Returns:
            The selected coordinates, or ``None`` when no legal move exists.

        Raises:
            ValueError: If the player or board representation is invalid.
            RuntimeError: If the native engine reports an error.
        """

        if player not in (1, 2):
            raise ValueError("player doit valoir 1 ou 2")
        if len(state.grid) != self.BOARD_SIZE or any(len(row) != self.BOARD_SIZE for row in state.grid):
            raise ValueError("le plateau doit mesurer 19x19")

        capture_scores = captures or {1: 0, 2: 0}
        flat = [cell for row in state.grid for cell in row]
        if any(cell not in (0, 1, 2) for cell in flat):
            raise ValueError("les cellules doivent valoir 0, 1 ou 2")
        native_board = (ctypes.c_uint8 * len(flat))(*flat)
        native_result = _NativeSearchResult()

        with self._lock:
            status = self._library.gomoku_find_best_move(
                self._engine,
                native_board,
                len(flat),
                player,
                int(capture_scores[1]),
                int(capture_scores[2]),
                max(1, int(budget_ms)),
                ctypes.byref(native_result),
            )

        self.last_search = SearchMetrics(
            score=native_result.score,
            completed_depth=native_result.completed_depth,
            nodes=native_result.nodes,
            elapsed_seconds=native_result.elapsed_us / 1_000_000,
            status=status,
        )
        if status == 2:
            return None
        if status != 0:
            raise RuntimeError(f"Le moteur Gomoku a échoué avec le statut {status}")
        return native_result.row, native_result.col
