#ifndef GOMOKU_ENGINE_HPP
#define GOMOKU_ENGINE_HPP

#include <array>
#include <chrono>
#include <cstdint>
#include <optional>
#include <vector>

namespace gomoku {

constexpr int BoardSize = 19;
constexpr int CellCount = BoardSize * BoardSize;
constexpr int WinScore = 10'000'000;

enum class Player : uint8_t { none = 0, one = 1, two = 2 };

struct Move {
    int index = -1;

    [[nodiscard]] int row() const { return index / BoardSize; }
    [[nodiscard]] int col() const { return index % BoardSize; }
    [[nodiscard]] bool valid() const { return index >= 0 && index < CellCount; }
    friend bool operator==(Move left, Move right) { return left.index == right.index; }
    friend bool operator!=(Move left, Move right) { return !(left == right); }
};

struct SearchResult {
    Move move;
    int score = 0;
    int completedDepth = 0;
    uint64_t nodes = 0;
    uint64_t elapsedMicroseconds = 0;
};

/// Information required to restore a board after a simulated move.
struct MoveUndo {
    Move move;
    Player player = Player::none;
    std::array<Move, 16> captured{};
    int capturedCount = 0;
    std::array<int, 2> previousCaptures{};
    uint64_t previousHash = 0;
};

class Board {
public:
    /// Create an empty 19 x 19 board.
    Board();

    /// Create a board from 361 row-major cells and both capture counters.
    /// @throws std::invalid_argument if a cell is not 0, 1, or 2.
    Board(const uint8_t *cells, int playerOneCaptures, int playerTwoCaptures);

    [[nodiscard]] Player at(Move move) const;
    [[nodiscard]] int captures(Player player) const;

    /// Return the Zobrist hash, including the side to move.
    [[nodiscard]] uint64_t hash(Player sideToMove) const;

    /// Estimate the position from the requested player's point of view.
    [[nodiscard]] int evaluation(Player perspective) const;

    /// Return whether placing a stone captures at least one opposing pair.
    [[nodiscard]] bool isCapturingMove(Move move, Player player) const;

    /// Return whether a move creates open threes on at least two axes.
    /// Capturing moves are exempt from the double-three restriction.
    [[nodiscard]] bool isDoubleThree(Move move, Player player) const;

    /// Check that a move is empty, on the board, and allowed by all rules.
    [[nodiscard]] bool isLegalMove(Move move, Player player) const;

    /// Return whether the player currently has five consecutive stones.
    [[nodiscard]] bool hasFive(Player player) const;

    /// Check capture and alignment victory conditions for the last player.
    [[nodiscard]] bool isWinningState(Player lastPlayer) const;

    /// Return whether the given move produced a victory that cannot be broken.
    [[nodiscard]] bool isWinningMove(Move move, Player player) const;

    /// Generate legal moves located within two cells of an existing stone.
    [[nodiscard]] std::vector<Move> legalMoves(Player player) const;

    /// Apply a legal move, remove captured pairs, and fill its undo record.
    /// @return false when the move is illegal; otherwise true.
    bool play(Move move, Player player, MoveUndo &undo);

    /// Restore the exact state saved by a previous call to play().
    void undo(const MoveUndo &undo);

    /// Recompute the complete heuristic score for consistency tests.
    [[nodiscard]] int fullEvaluation(Player perspective) const;
    [[nodiscard]] const std::array<uint8_t, CellCount> &cells() const { return cells_; }

private:
    static constexpr int MaxLines = 128;
    struct Line {
        std::array<int, BoardSize> cells{};
        int length = 0;
    };

    std::array<uint8_t, CellCount> cells_{};
    std::array<std::array<uint64_t, 6>, 2> stones_{};
    std::array<int, 2> captures_{};
    std::array<Line, MaxLines> lines_{};
    std::array<std::array<int, 4>, CellCount> cellLines_{};
    std::array<int, MaxLines> lineScores_{};
    int lineCount_ = 0;
    int totalScore_ = 0;
    uint64_t hash_ = 0;

    static Player opponent(Player player);
    static bool inside(int row, int col);
    static uint64_t pieceKey(int index, Player player);
    static uint64_t captureKey(Player player, int captures);
    static uint64_t sideKey(Player player);

    void initializeLines();
    void rebuildDerivedState();
    void setCell(Move move, Player player);
    void refreshLines(const std::vector<Move> &changed);
    [[nodiscard]] int scoreLine(const Line &line) const;
    [[nodiscard]] bool hasFiveThrough(Move move, Player player) const;
    [[nodiscard]] bool directionHasOpenThree(Move move, Player player, int dr, int dc) const;
    [[nodiscard]] bool hasBreakingCapture(Player alignedPlayer) const;
};

class Engine {
public:
    Engine();

    /// Search for the best legal move within the supplied time budget.
    ///
    /// The result contains the last fully completed depth. A value of zero
    /// means that an opening or direct tactical rule selected the move.
    SearchResult findBestMove(Board board, Player player, int budgetMilliseconds);

private:
    enum class Bound : uint8_t { exact, lower, upper };
    struct Entry {
        uint64_t key = 0;
        int score = 0;
        int depth = -1;
        Move bestMove;
        Bound bound = Bound::exact;
        uint16_t generation = 0;
    };
    struct Timeout {};

    std::vector<Entry> table_;
    std::array<std::array<Move, 2>, 64> killers_{};
    std::array<std::array<int, CellCount>, 2> history_{};
    std::chrono::steady_clock::time_point deadline_{};
    uint64_t nodes_ = 0;
    uint16_t generation_ = 0;
    int iterationDepth_ = 0;

    /// Evaluate a search subtree with Negamax and alpha-beta pruning.
    int negamax(Board &board, Player player, int depth, int ply, int alpha, int beta, Move previousMove);

    /// Sort legal moves so likely cutoffs and tactical moves are searched first.
    std::vector<Move> orderedMoves(Board &board, Player player, int ply, Move transpositionMove);

    /// Compute the ordering score of one move without keeping it on the board.
    int movePriority(Board &board, Move move, Player player, int ply, Move transpositionMove);

    /// Return how many ordered moves may be searched at this level.
    int branchLimit(int ply, int available) const;

    /// Abort the current iterative-deepening pass when its deadline expires.
    void checkDeadline();

    /// Find a transposition entry only when its complete key matches.
    Entry *probe(uint64_t key);

    /// Save a transposition result when it is new or at least as deep.
    void store(uint64_t key, int depth, int score, Bound bound, Move bestMove);
    static Player opponent(Player player);
};

} // namespace gomoku

#endif
