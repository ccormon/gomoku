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
    Board();
    Board(const uint8_t *cells, int playerOneCaptures, int playerTwoCaptures);

    [[nodiscard]] Player at(Move move) const;
    [[nodiscard]] int captures(Player player) const;
    [[nodiscard]] uint64_t hash(Player sideToMove) const;
    [[nodiscard]] int evaluation(Player perspective) const;
    [[nodiscard]] bool isCapturingMove(Move move, Player player) const;
    [[nodiscard]] bool isDoubleThree(Move move, Player player) const;
    [[nodiscard]] bool isLegalMove(Move move, Player player) const;
    [[nodiscard]] bool hasFive(Player player) const;
    [[nodiscard]] bool isWinningState(Player lastPlayer) const;
    [[nodiscard]] bool isWinningMove(Move move, Player player) const;
    [[nodiscard]] std::vector<Move> legalMoves(Player player) const;

    bool play(Move move, Player player, MoveUndo &undo);
    void undo(const MoveUndo &undo);

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

    int negamax(Board &board, Player player, int depth, int ply, int alpha, int beta, Move previousMove);
    std::vector<Move> orderedMoves(Board &board, Player player, int ply, Move transpositionMove);
    int movePriority(Board &board, Move move, Player player, int ply, Move transpositionMove);
    int branchLimit(int ply, int available) const;
    void checkDeadline();
    Entry *probe(uint64_t key);
    void store(uint64_t key, int depth, int score, Bound bound, Move bestMove);
    static Player opponent(Player player);
};

} // namespace gomoku

#endif
