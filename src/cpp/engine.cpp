#include "gomoku/engine.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <string_view>

namespace gomoku {
namespace {

constexpr std::array<std::pair<int, int>, 8> Directions{{
    {0, 1}, {0, -1}, {1, 0}, {-1, 0}, {1, 1}, {-1, -1}, {1, -1}, {-1, 1}
}};
constexpr std::array<std::pair<int, int>, 4> Axes{{
    {0, 1}, {1, 0}, {1, 1}, {1, -1}
}};

uint64_t mix(uint64_t value) {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31U);
}

int playerIndex(Player player) {
    return static_cast<int>(player) - 1;
}

struct HeuristicPattern {
    std::string_view cells;
    int score;
};


constexpr std::array<HeuristicPattern, 28> HeuristicPatterns{{
    {"11111", 2'000'000},
    {"011110", 100'000},
    {"101110", 50'000},
    {"011101", 50'000},
    {"0110110", 40'000},
    {"311101", 10'000},
    {"101113", 10'000},
    {"311110", 10'000},
    {"011113", 10'000},
    {"01110", 5'000},
    {"010110", 3'000},
    {"011010", 3'000},
    {"31110", 1'000},
    {"01113", 1'000},
    {"311010", 500},
    {"010113", 500},
    {"0110", 300},
    {"01010", 300},
    {"3110", 80},
    {"0113", 80},
    {"31010", 40},
    {"01013", 40},
    {"010", 20},
    {"310", 10},
    {"013", 10},
    {"3113", 10},
    {"31113", 50},
    {"311113", 100},
}};

const std::array<std::array<int, 1U << 14U>, 8> &heuristicScoreTable() {
    static const std::array<std::array<int, 1U << 14U>, 8> table = [] {
        std::array<std::array<int, 1U << 14U>, 8> result{};
        for (const HeuristicPattern &pattern : HeuristicPatterns) {
            int code = 0;
            for (char cell : pattern.cells) {
                code = code * 4 + (cell - '0');
            }
            result[pattern.cells.size()][code] = pattern.score;
        }
        return result;
    }();
    return table;
}

} // namespace

Board::Board() {
    initializeLines();
    rebuildDerivedState();
}

Board::Board(const uint8_t *cells, int playerOneCaptures, int playerTwoCaptures) {
    initializeLines();
    for (int index = 0; index < CellCount; ++index) {
        if (cells[index] > 2) {
            throw std::invalid_argument("board cells must be 0, 1, or 2");
        }
        cells_[index] = cells[index];
    }
    captures_[0] = std::clamp(playerOneCaptures, 0, 10);
    captures_[1] = std::clamp(playerTwoCaptures, 0, 10);
    rebuildDerivedState();
}

Player Board::opponent(Player player) {
    return player == Player::one ? Player::two : Player::one;
}

bool Board::inside(int row, int col) {
    return row >= 0 && row < BoardSize && col >= 0 && col < BoardSize;
}

uint64_t Board::pieceKey(int index, Player player) {
    return mix(0x1000ULL + static_cast<uint64_t>(index * 2 + playerIndex(player)));
}

uint64_t Board::captureKey(Player player, int captures) {
    return mix(0x4000ULL + static_cast<uint64_t>(playerIndex(player) * 11 + captures));
}

uint64_t Board::sideKey(Player player) {
    return mix(0x8000ULL + static_cast<uint64_t>(playerIndex(player)));
}

void Board::initializeLines() {
    for (auto &ids : cellLines_) {
        ids.fill(-1);
    }
    auto addLine = [this](int row, int col, int dr, int dc) {
        Line line;
        while (inside(row, col)) {
            line.cells[line.length++] = row * BoardSize + col;
            row += dr;
            col += dc;
        }
        if (line.length < 2) {
            return;
        }
        const int id = lineCount_++;
        lines_[id] = line;
        for (int offset = 0; offset < line.length; ++offset) {
            auto &ids = cellLines_[line.cells[offset]];
            *std::find(ids.begin(), ids.end(), -1) = id;
        }
    };

    for (int i = 0; i < BoardSize; ++i) {
        addLine(i, 0, 0, 1);
        addLine(0, i, 1, 0);
    }
    for (int col = 0; col < BoardSize; ++col) {
        addLine(0, col, 1, 1);
        addLine(0, col, 1, -1);
    }
    for (int row = 1; row < BoardSize; ++row) {
        addLine(row, 0, 1, 1);
        addLine(row, BoardSize - 1, 1, -1);
    }
}

void Board::rebuildDerivedState() {
    stones_ = {};
    hash_ = captureKey(Player::one, captures_[0]) ^ captureKey(Player::two, captures_[1]);
    for (int index = 0; index < CellCount; ++index) {
        const Player player = static_cast<Player>(cells_[index]);
        if (player == Player::none) {
            continue;
        }
        stones_[playerIndex(player)][index / 64] |= 1ULL << (index % 64);
        hash_ ^= pieceKey(index, player);
    }
    totalScore_ = 0;
    for (int id = 0; id < lineCount_; ++id) {
        lineScores_[id] = scoreLine(lines_[id]);
        totalScore_ += lineScores_[id];
    }
}

Player Board::at(Move move) const {
    return move.valid() ? static_cast<Player>(cells_[move.index]) : Player::none;
}

int Board::captures(Player player) const {
    return captures_[playerIndex(player)];
}

uint64_t Board::hash(Player sideToMove) const {
    return hash_ ^ sideKey(sideToMove);
}

int Board::evaluation(Player perspective) const {
    // Une paire capturée vaut 30 000, soit 15 000 par pierre.
    const int captureScore = (captures_[0] - captures_[1]) * 15'000;
    const int score = totalScore_ + captureScore;
    return perspective == Player::one ? score : -score;
}

int Board::scoreLine(const Line &line) const {
    int score = 0;
    const auto &patternScores = heuristicScoreTable();
    for (Player player : {Player::one, Player::two}) {
        const int sign = player == Player::one ? 1 : -1;
        const uint8_t stone = static_cast<uint8_t>(player);
        std::array<uint8_t, BoardSize + 2> encoded{};
        encoded[0] = 3;
        for (int position = 0; position < line.length; ++position) {
            const uint8_t actual = cells_[line.cells[position]];
            encoded[position + 1] = actual == 0 ? 0 : (actual == stone ? 1 : 3);
        }
        encoded[line.length + 1] = 3;

        const int encodedLength = line.length + 2;
        for (int start = 0; start < encodedLength; ++start) {
            int code = 0;
            const int maxLength = std::min(7, encodedLength - start);
            for (int length = 1; length <= maxLength; ++length) {
                code = code * 4 + encoded[start + length - 1];
                score += sign * patternScores[length][code];
            }
        }
    }
    return score;
}

void Board::setCell(Move move, Player player) {
    const Player previous = at(move);
    if (previous != Player::none) {
        stones_[playerIndex(previous)][move.index / 64] &= ~(1ULL << (move.index % 64));
        hash_ ^= pieceKey(move.index, previous);
    }
    cells_[move.index] = static_cast<uint8_t>(player);
    if (player != Player::none) {
        stones_[playerIndex(player)][move.index / 64] |= 1ULL << (move.index % 64);
        hash_ ^= pieceKey(move.index, player);
    }
}

void Board::refreshLines(const std::vector<Move> &changed) {
    std::array<bool, MaxLines> dirty{};
    for (Move move : changed) {
        for (int id : cellLines_[move.index]) {
            if (id >= 0) {
                dirty[id] = true;
            }
        }
    }
    for (int id = 0; id < lineCount_; ++id) {
        if (!dirty[id]) {
            continue;
        }
        totalScore_ -= lineScores_[id];
        lineScores_[id] = scoreLine(lines_[id]);
        totalScore_ += lineScores_[id];
    }
}

bool Board::isCapturingMove(Move move, Player player) const {
    if (!move.valid() || at(move) != Player::none) {
        return false;
    }
    const Player enemy = opponent(player);
    for (const auto &[dr, dc] : Directions) {
        const int row = move.row();
        const int col = move.col();
        if (!inside(row + 3 * dr, col + 3 * dc)) {
            continue;
        }
        const Move one{(row + dr) * BoardSize + col + dc};
        const Move two{(row + 2 * dr) * BoardSize + col + 2 * dc};
        const Move three{(row + 3 * dr) * BoardSize + col + 3 * dc};
        if (at(one) == enemy && at(two) == enemy && at(three) == player) {
            return true;
        }
    }
    return false;
}

bool Board::directionHasOpenThree(Move move, Player player, int dr, int dc) const {
    std::array<uint8_t, 11> values{};
    for (int offset = -5; offset <= 5; ++offset) {
        const int row = move.row() + offset * dr;
        const int col = move.col() + offset * dc;
        values[offset + 5] = inside(row, col) ? cells_[row * BoardSize + col] : 3;
    }
    values[5] = static_cast<uint8_t>(player);

    for (int completion = 1; completion < 10; ++completion) {
        if (completion == 5 || values[completion] != 0) {
            continue;
        }
        values[completion] = static_cast<uint8_t>(player);
        for (int start = 0; start + 5 < 11; ++start) {
            if (values[start] != 0 || values[start + 5] != 0) {
                continue;
            }
            bool openFour = true;
            for (int cell = start + 1; cell < start + 5; ++cell) {
                openFour &= values[cell] == static_cast<uint8_t>(player);
            }
            const bool containsMove = 5 > start && 5 < start + 5;
            const bool containsCompletion = completion > start && completion < start + 5;
            if (openFour && containsMove && containsCompletion) {
                values[completion] = 0;
                return true;
            }
        }
        values[completion] = 0;
    }
    return false;
}

bool Board::isDoubleThree(Move move, Player player) const {
    if (!move.valid() || at(move) != Player::none || isCapturingMove(move, player)) {
        return false;
    }
    int openThrees = 0;
    for (const auto &[dr, dc] : Axes) {
        openThrees += directionHasOpenThree(move, player, dr, dc);
    }
    return openThrees >= 2;
}

bool Board::isLegalMove(Move move, Player player) const {
    return move.valid() && player != Player::none && at(move) == Player::none
        && !isDoubleThree(move, player);
}

bool Board::play(Move move, Player player, MoveUndo &undo) {
    if (!isLegalMove(move, player)) {
        return false;
    }
    undo = {};
    undo.move = move;
    undo.player = player;
    undo.previousCaptures = captures_;
    undo.previousHash = hash_;

    std::vector<Move> changed{move};
    setCell(move, player);
    const Player enemy = opponent(player);
    for (const auto &[dr, dc] : Directions) {
        const int row = move.row();
        const int col = move.col();
        if (!inside(row + 3 * dr, col + 3 * dc)) {
            continue;
        }
        const Move one{(row + dr) * BoardSize + col + dc};
        const Move two{(row + 2 * dr) * BoardSize + col + 2 * dc};
        const Move three{(row + 3 * dr) * BoardSize + col + 3 * dc};
        if (at(one) == enemy && at(two) == enemy && at(three) == player) {
            undo.captured[undo.capturedCount++] = one;
            undo.captured[undo.capturedCount++] = two;
            changed.push_back(one);
            changed.push_back(two);
            setCell(one, Player::none);
            setCell(two, Player::none);
        }
    }
    const int index = playerIndex(player);
    hash_ ^= captureKey(player, captures_[index]);
    captures_[index] = std::min(10, captures_[index] + undo.capturedCount);
    hash_ ^= captureKey(player, captures_[index]);
    refreshLines(changed);
    return true;
}

void Board::undo(const MoveUndo &undo) {
    std::vector<Move> changed{undo.move};
    setCell(undo.move, Player::none);
    const Player enemy = opponent(undo.player);
    for (int index = 0; index < undo.capturedCount; ++index) {
        setCell(undo.captured[index], enemy);
        changed.push_back(undo.captured[index]);
    }
    captures_ = undo.previousCaptures;
    hash_ = undo.previousHash;
    refreshLines(changed);
}

bool Board::hasFive(Player player) const {
    for (int id = 0; id < lineCount_; ++id) {
        int run = 0;
        for (int offset = 0; offset < lines_[id].length; ++offset) {
            run = cells_[lines_[id].cells[offset]] == static_cast<uint8_t>(player) ? run + 1 : 0;
            if (run >= 5) {
                return true;
            }
        }
    }
    return false;
}

bool Board::hasFiveThrough(Move move, Player player) const {
    if (!move.valid() || at(move) != player) {
        return false;
    }
    for (int id : cellLines_[move.index]) {
        if (id < 0) continue;
        int run = 0;
        for (int offset = 0; offset < lines_[id].length; ++offset) {
            run = cells_[lines_[id].cells[offset]] == static_cast<uint8_t>(player) ? run + 1 : 0;
            if (run >= 5) return true;
        }
    }
    return false;
}

bool Board::hasBreakingCapture(Player alignedPlayer) const {
    const Player defender = opponent(alignedPlayer);
    for (int index = 0; index < CellCount; ++index) {
        Move move{index};
        if (!isCapturingMove(move, defender) || !isLegalMove(move, defender)) {
            continue;
        }
        Board reply = *this;
        MoveUndo undo;
        reply.play(move, defender, undo);
        if (reply.captures(defender) >= 10 || !reply.hasFive(alignedPlayer)) {
            return true;
        }
    }
    return false;
}

bool Board::isWinningState(Player lastPlayer) const {
    if (captures(lastPlayer) >= 10) {
        return true;
    }
    return hasFive(lastPlayer) && !hasBreakingCapture(lastPlayer);
}

bool Board::isWinningMove(Move move, Player player) const {
    if (captures(player) >= 10) {
        return true;
    }
    return hasFiveThrough(move, player) && !hasBreakingCapture(player);
}

std::vector<Move> Board::legalMoves(Player player) const {
    std::array<bool, CellCount> candidate{};
    bool occupied = false;
    for (int index = 0; index < CellCount; ++index) {
        if (cells_[index] == 0) {
            continue;
        }
        occupied = true;
        const int row = index / BoardSize;
        const int col = index % BoardSize;
        for (int dr = -2; dr <= 2; ++dr) {
            for (int dc = -2; dc <= 2; ++dc) {
                if (inside(row + dr, col + dc)) {
                    candidate[(row + dr) * BoardSize + col + dc] = true;
                }
            }
        }
    }
    if (!occupied) {
        return {{CellCount / 2}};
    }
    std::vector<Move> moves;
    moves.reserve(96);
    for (int index = 0; index < CellCount; ++index) {
        Move move{index};
        if (candidate[index] && isLegalMove(move, player)) {
            moves.push_back(move);
        }
    }
    return moves;
}

int Board::fullEvaluation(Player perspective) const {
    int score = 0;
    for (int id = 0; id < lineCount_; ++id) {
        score += scoreLine(lines_[id]);
    }
    score += (captures_[0] - captures_[1]) * 15'000;
    return perspective == Player::one ? score : -score;
}

Engine::Engine() : table_(1U << 18U) {}

Player Engine::opponent(Player player) {
    return player == Player::one ? Player::two : Player::one;
}

void Engine::checkDeadline() {
    if (std::chrono::steady_clock::now() >= deadline_) {
        throw Timeout{};
    }
}

Engine::Entry *Engine::probe(uint64_t key) {
    Entry &entry = table_[key & (table_.size() - 1)];
    return entry.key == key ? &entry : nullptr;
}

void Engine::store(uint64_t key, int depth, int score, Bound bound, Move bestMove) {
    Entry &entry = table_[key & (table_.size() - 1)];
    if (entry.generation != generation_ || depth >= entry.depth) {
        entry = {key, score, depth, bestMove, bound, generation_};
    }
}

int Engine::movePriority(Board &board, Move move, Player player, int ply, Move transpositionMove) {
    int priority = history_[playerIndex(player)][move.index];
    if (move == transpositionMove) priority += 4'000'000;
    if (ply < static_cast<int>(killers_.size()) && move == killers_[ply][0]) priority += 500'000;
    if (ply < static_cast<int>(killers_.size()) && move == killers_[ply][1]) priority += 250'000;

    MoveUndo undo;
    const int beforeCaptures = board.captures(player);
    const int beforeEvaluation = board.evaluation(player);
    board.play(move, player, undo);
    if (board.isWinningMove(move, player)) priority += 20'000'000;
    priority += (board.captures(player) - beforeCaptures) * 400'000;
    priority += board.evaluation(player) - beforeEvaluation;
    board.undo(undo);

    const Player enemy = opponent(player);
    if (board.isLegalMove(move, enemy)) {
        MoveUndo enemyUndo;
        const int enemyBeforeEvaluation = board.evaluation(enemy);
        board.play(move, enemy, enemyUndo);
        if (board.isWinningMove(move, enemy)) priority += 10'000'000;
        // Une case qui permettrait une forte menace adverse est prioritaire en
        // défense. Le facteur 2 évite qu'une attaque secondaire masque un
        // quatre ouvert ou un trois cassé à neutraliser immédiatement.
        priority += 2 * (board.evaluation(enemy) - enemyBeforeEvaluation);
        board.undo(enemyUndo);
    }
    return priority;
}

std::vector<Move> Engine::orderedMoves(Board &board, Player player, int ply, Move transpositionMove) {
    auto moves = board.legalMoves(player);
    std::vector<std::pair<int, Move>> ranked;
    ranked.reserve(moves.size());
    for (Move move : moves) {
        checkDeadline();
        ranked.emplace_back(movePriority(board, move, player, ply, transpositionMove), move);
    }
    std::sort(ranked.begin(), ranked.end(), [](const auto &left, const auto &right) {
        return left.first != right.first ? left.first > right.first : left.second.index < right.second.index;
    });
    moves.clear();
    for (const auto &[priority, move] : ranked) {
        (void)priority;
        moves.push_back(move);
    }
    return moves;
}

int Engine::branchLimit(int ply, int available) const {
    if (iterationDepth_ >= 8) {
        if (ply == 0) return std::min(16, available);
        if (ply == 1) return std::min(6, available);
        if (ply <= 3) return std::min(3, available);
        return std::min(1, available);
    }
    if (ply == 0) return std::min(16, available);
    if (ply == 1) return std::min(10, available);
    return std::min(6, available);
}

int Engine::negamax(Board &board, Player player, int depth, int ply, int alpha, int beta, Move previousMove) {
    ++nodes_;
    checkDeadline();
    const Player previous = opponent(player);
    if (board.isWinningMove(previousMove, previous)) return -WinScore + ply;
    if (board.hasFive(player)) return WinScore - ply;
    if (depth == 0) return board.evaluation(player);

    const uint64_t key = board.hash(player);
    const int originalAlpha = alpha;
    Move transpositionMove;
    if (Entry *entry = probe(key)) {
        transpositionMove = entry->bestMove;
        if (entry->depth >= depth) {
            if (entry->bound == Bound::exact) return entry->score;
            if (entry->bound == Bound::lower) alpha = std::max(alpha, entry->score);
            if (entry->bound == Bound::upper) beta = std::min(beta, entry->score);
            if (alpha >= beta) return entry->score;
        }
    }

    auto moves = orderedMoves(board, player, ply, transpositionMove);
    if (moves.empty()) return board.evaluation(player);
    moves.resize(branchLimit(ply, static_cast<int>(moves.size())));

    int bestScore = -WinScore;
    Move bestMove = moves.front();
    for (Move move : moves) {
        MoveUndo undo;
        board.play(move, player, undo);
        const int score = -negamax(board, opponent(player), depth - 1, ply + 1, -beta, -alpha, move);
        board.undo(undo);
        if (score > bestScore) {
            bestScore = score;
            bestMove = move;
        }
        alpha = std::max(alpha, score);
        if (alpha >= beta) {
            history_[playerIndex(player)][move.index] += depth * depth;
            if (ply < static_cast<int>(killers_.size()) && killers_[ply][0] != move) {
                killers_[ply][1] = killers_[ply][0];
                killers_[ply][0] = move;
            }
            break;
        }
    }
    const Bound bound = bestScore <= originalAlpha ? Bound::upper
        : (bestScore >= beta ? Bound::lower : Bound::exact);
    store(key, depth, bestScore, bound, bestMove);
    return bestScore;
}

SearchResult Engine::findBestMove(Board board, Player player, int budgetMilliseconds) {
    const auto started = std::chrono::steady_clock::now();
    deadline_ = started + std::chrono::milliseconds(std::max(1, budgetMilliseconds));
    nodes_ = 0;
    ++generation_;
    SearchResult result;
    auto legal = board.legalMoves(player);
    if (legal.empty()) {
        result.elapsedMicroseconds = 0;
        return result;
    }
    result.move = legal.front();
    if (legal.size() == 1) {
        result.elapsedMicroseconds = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - started).count()
        );
        return result;
    }

    // Conserver des résultats intermédiaires solides lorsque la position est
    // trop complexe pour terminer directement la recherche tactique profondeur 10.
    std::vector<int> depths{1, 2, 3, 4, 10};
    for (int depth = 11; depth <= 32; ++depth) depths.push_back(depth);
    for (int depth : depths) {
        iterationDepth_ = depth;
        try {
            auto moves = orderedMoves(board, player, 0, result.move);
            moves.resize(branchLimit(0, static_cast<int>(moves.size())));
            int bestScore = -WinScore;
            Move bestMove = moves.front();
            int alpha = -WinScore;
            for (Move move : moves) {
                checkDeadline();
                MoveUndo undo;
                board.play(move, player, undo);
                const int score = -negamax(board, opponent(player), depth - 1, 1, -WinScore, -alpha, move);
                board.undo(undo);
                if (score > bestScore) {
                    bestScore = score;
                    bestMove = move;
                }
                alpha = std::max(alpha, score);
            }
            result.move = bestMove;
            result.score = bestScore;
            result.completedDepth = depth;
            if (std::abs(bestScore) >= WinScore - 64) break;
        } catch (const Timeout &) {
            break;
        }
    }
    result.nodes = nodes_;
    result.elapsedMicroseconds = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - started).count()
    );
    return result;
}

} // namespace gomoku
