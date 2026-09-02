#include "gomoku/engine.hpp"

#include <array>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>

using gomoku::Board;
using gomoku::CellCount;
using gomoku::Engine;
using gomoku::Move;
using gomoku::MoveUndo;
using gomoku::Player;

namespace {

int failures = 0;

Move moveAt(int row, int col) {
    return {row * gomoku::BoardSize + col};
}

void expect(bool condition, const std::string &message) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << message << '\n';
    }
}

Board makeBoard(const std::array<uint8_t, CellCount> &cells, int capturesOne = 0, int capturesTwo = 0) {
    return Board(cells.data(), capturesOne, capturesTwo);
}

void testCaptureAndUndo() {
    std::array<uint8_t, CellCount> cells{};
    cells[moveAt(9, 10).index] = 2;
    cells[moveAt(9, 11).index] = 2;
    cells[moveAt(9, 12).index] = 1;
    Board board = makeBoard(cells);
    const auto initialHash = board.hash(Player::one);
    const auto initialEvaluation = board.evaluation(Player::one);
    MoveUndo undo;
    expect(board.play(moveAt(9, 9), Player::one, undo), "capture move is legal");
    expect(undo.capturedCount == 2, "exactly one pair is captured");
    expect(board.at(moveAt(9, 10)) == Player::none, "first captured stone is removed");
    expect(board.captures(Player::one) == 2, "capture counter counts stones");
    expect(board.evaluation(Player::one) == board.fullEvaluation(Player::one), "incremental evaluation matches full evaluation");
    board.undo(undo);
    expect(board.cells() == cells, "undo restores every cell");
    expect(board.hash(Player::one) == initialHash, "undo restores zobrist hash");
    expect(board.evaluation(Player::one) == initialEvaluation, "undo restores evaluation");
}

void testMultipleCapture() {
    std::array<uint8_t, CellCount> cells{};
    for (const auto &[row, col] : std::array<std::pair<int, int>, 4>{{{9, 10}, {9, 11}, {10, 9}, {11, 9}}}) {
        cells[moveAt(row, col).index] = 2;
    }
    cells[moveAt(9, 12).index] = 1;
    cells[moveAt(12, 9).index] = 1;
    Board board = makeBoard(cells);
    MoveUndo undo;
    board.play(moveAt(9, 9), Player::one, undo);
    expect(undo.capturedCount == 4, "one move captures pairs in multiple directions");
    expect(board.captures(Player::one) == 4, "multiple captures update score once");
}

void testDoubleThreeAndCaptureException() {
    std::array<uint8_t, CellCount> cells{};
    for (const auto &[row, col] : std::array<std::pair<int, int>, 4>{{{9, 8}, {9, 10}, {8, 9}, {10, 9}}}) {
        cells[moveAt(row, col).index] = 1;
    }
    Board board = makeBoard(cells);
    expect(board.isDoubleThree(moveAt(9, 9), Player::one), "cross creates two free threes");
    expect(!board.isLegalMove(moveAt(9, 9), Player::one), "double three is forbidden");

    cells = {};
    for (const auto &[row, col] : std::array<std::pair<int, int>, 4>{{{8, 9}, {10, 9}, {8, 8}, {10, 10}}}) {
        cells[moveAt(row, col).index] = 1;
    }
    cells[moveAt(9, 10).index] = 2;
    cells[moveAt(9, 11).index] = 2;
    cells[moveAt(9, 12).index] = 1;
    board = makeBoard(cells);
    expect(board.isCapturingMove(moveAt(9, 9), Player::one), "exception move captures a pair");
    expect(!board.isDoubleThree(moveAt(9, 9), Player::one), "capture exempts a double three");
    expect(board.isLegalMove(moveAt(9, 9), Player::one), "capturing double three remains legal");
}

void testWins() {
    std::array<uint8_t, CellCount> cells{};
    for (int col = 5; col <= 9; ++col) cells[moveAt(9, col).index] = 1;
    Board safe = makeBoard(cells);
    expect(safe.hasFive(Player::one), "five or more is detected");
    expect(safe.isWinningState(Player::one), "uncapturable five wins");

    cells[moveAt(10, 7).index] = 1;
    cells[moveAt(8, 7).index] = 2;
    Board breakable = makeBoard(cells);
    expect(!breakable.isWinningState(Player::one), "capturable five does not win yet");

    cells = {};
    cells[moveAt(9, 10).index] = 2;
    cells[moveAt(9, 11).index] = 2;
    cells[moveAt(9, 12).index] = 1;
    Board captureWin = makeBoard(cells, 8, 0);
    MoveUndo undo;
    captureWin.play(moveAt(9, 9), Player::one, undo);
    expect(captureWin.isWinningState(Player::one), "tenth captured stone wins");

    cells = {};
    for (int col = 5; col <= 9; ++col) cells[moveAt(9, col).index] = 1;
    cells[moveAt(3, 4).index] = 1;
    cells[moveAt(3, 5).index] = 1;
    cells[moveAt(3, 6).index] = 2;
    Board captureReply = makeBoard(cells, 0, 8);
    expect(!captureReply.isWinningState(Player::one), "a fifth capture available anywhere defers alignment victory");
}

void testIncrementalStateSequence() {
    Board board;
    std::vector<MoveUndo> undos;
    Player player = Player::one;
    std::mt19937 generator(42);
    for (int turn = 0; turn < 30; ++turn) {
        auto moves = board.legalMoves(player);
        expect(!moves.empty(), "random sequence always has a legal move");
        std::uniform_int_distribution<std::size_t> choice(0, moves.size() - 1);
        MoveUndo undo;
        board.play(moves[choice(generator)], player, undo);
        undos.push_back(undo);
        expect(board.evaluation(Player::one) == board.fullEvaluation(Player::one), "incremental score stays exact during play");
        player = player == Player::one ? Player::two : Player::one;
    }
    while (!undos.empty()) {
        board.undo(undos.back());
        undos.pop_back();
        expect(board.evaluation(Player::one) == board.fullEvaluation(Player::one), "incremental score stays exact during undo");
    }
    expect(board.cells() == Board().cells(), "undo sequence restores empty board");
}

void testPatternHeuristic() {
    std::array<uint8_t, CellCount> cells{};
    for (int col = 7; col <= 10; ++col) cells[moveAt(9, col).index] = 1;
    const Board openFour = makeBoard(cells);

    cells[moveAt(9, 6).index] = 2;
    const Board blockedFour = makeBoard(cells);
    expect(openFour.evaluation(Player::one) > blockedFour.evaluation(Player::one),
        "heuristic strongly prefers an open four to a blocked four");
    expect(openFour.evaluation(Player::one) >= 100'000,
        "open-four pattern keeps its 100000 tactical weight");

    cells = {};
    for (int col : {7, 8, 10}) cells[moveAt(9, col).index] = 1;
    const Board brokenThree = makeBoard(cells);
    cells = {};
    for (int col : {7, 8}) cells[moveAt(9, col).index] = 1;
    const Board openTwo = makeBoard(cells);
    expect(brokenThree.evaluation(Player::one) > openTwo.evaluation(Player::one),
        "broken-three patterns outrank an open two");

    cells = {};
    const Board noCaptures = makeBoard(cells, 0, 0);
    const Board oneCapturedPair = makeBoard(cells, 2, 0);
    expect(oneCapturedPair.evaluation(Player::one) - noCaptures.evaluation(Player::one) == 30'000,
        "capture heuristic awards 30000 per captured pair");
}

void testSearch() {
    std::array<uint8_t, CellCount> cells{};
    for (int col = 5; col <= 8; ++col) cells[moveAt(9, col).index] = 1;
    cells[moveAt(9, 4).index] = 2;
    Board board = makeBoard(cells);
    Engine engine;
    const auto result = engine.findBestMove(board, Player::one, 450);
    expect(result.move == moveAt(9, 9), "search takes an immediate alignment win");
    expect(result.elapsedMicroseconds <= 500'000, "search honors integration time margin");

    Board empty;
    const auto opening = engine.findBestMove(empty, Player::one, 450);
    expect(opening.move == moveAt(9, 9), "opening move is the center");
    expect(opening.completedDepth == 0, "opening book does not claim searched plies");

    cells = {};
    for (int col = 5; col <= 8; ++col) cells[moveAt(9, col).index] = 2;
    cells[moveAt(9, 4).index] = 1;
    Board defense = makeBoard(cells);
    const auto blocking = engine.findBestMove(defense, Player::one, 450);
    expect(blocking.move == moveAt(9, 9), "search blocks an immediate loss");

    cells = {};
    for (int col = 5; col <= 8; ++col) cells[moveAt(12, col).index] = 2;
    cells[moveAt(12, 4).index] = 1;
    for (int col = 5; col <= 7; ++col) cells[moveAt(4, col).index] = 1;
    Board urgentDefense = makeBoard(cells);
    const auto urgentBlocking = engine.findBestMove(urgentDefense, Player::one, 1);
    expect(urgentBlocking.move == moveAt(12, 9),
        "an immediate opposing win is blocked before extending an attacking three");

    // Exact position after the first nine moves of the reported game. Player
    // two must complete its edge-aligned five before considering a block.
    cells = {};
    for (int row : {15, 16, 17, 18}) cells[moveAt(row, 9).index] = 2;
    for (int row : {15, 16, 17, 18}) cells[moveAt(row, 11).index] = 1;
    cells[moveAt(17, 10).index] = 1;
    Board reportedImmediateWin = makeBoard(cells);
    for (int budget : {1, 10, 100, 450}) {
        const auto winningMove = engine.findBestMove(reportedImmediateWin, Player::two, budget);
        expect(winningMove.move == moveAt(14, 9),
            "reported position takes its own immediate win before blocking");
    }
    MoveUndo winningUndo;
    reportedImmediateWin.play(moveAt(14, 9), Player::two, winningUndo);
    expect(reportedImmediateWin.isWinningState(Player::two),
        "reported fifth stone is an immediate, unbreakable win");

    // Both players have four stones. Player two's breakable five must be
    // preferred because it forces player one to answer with a capture.
    cells = {};
    for (int row : {15, 16, 17, 18}) {
        cells[moveAt(row, 9).index] = 1;
        cells[moveAt(row, 7).index] = 2;
    }
    cells[moveAt(17, 8).index] = 2;
    Board competingFours = makeBoard(cells);
    MoveUndo breakableFiveUndo;
    competingFours.play(moveAt(14, 7), Player::two, breakableFiveUndo);
    expect(competingFours.hasFive(Player::two),
        "offensive continuation completes player two's five");
    expect(!competingFours.isWinningState(Player::two),
        "player two's five can still be broken by capture");
    expect(competingFours.isCapturingMove(moveAt(17, 6), Player::one),
        "player one has the reported capture reply");
    competingFours.undo(breakableFiveUndo);
    for (int budget : {1, 10, 100, 450}) {
        const auto offensiveMove = engine.findBestMove(competingFours, Player::two, budget);
        expect(offensiveMove.move == moveAt(14, 7),
            "own breakable five is preferred to blocking the opposing four");
    }

    // Breakable-five variant: a defensive capture must not make an unrelated
    // attacking extension rank ahead of the required block.
    cells = {};
    for (int row : {15, 16, 17, 18}) cells[moveAt(row, 9).index] = 1;
    cells[moveAt(17, 8).index] = 1;
    for (int row : {16, 17, 18}) cells[moveAt(row, 7).index] = 2;
    cells[moveAt(5, 9).index] = 2;
    Board reportedCapturePosition = makeBoard(cells);
    expect(reportedCapturePosition.isCapturingMove(moveAt(17, 10), Player::two),
        "reported position contains the defensive capture");
    for (int budget : {1, 10, 100, 450}) {
        const auto reportedDefense = engine.findBestMove(reportedCapturePosition, Player::two, budget);
        expect(reportedDefense.move == moveAt(14, 9),
            "reported four is blocked consistently even when a defensive capture exists");
    }

    MoveUndo alignmentUndo;
    reportedCapturePosition.play(moveAt(14, 9), Player::one, alignmentUndo);
    expect(reportedCapturePosition.hasFive(Player::one),
        "reported continuation creates the expected breakable five");
    const auto lastChanceCapture = engine.findBestMove(reportedCapturePosition, Player::two, 1);
    expect(reportedCapturePosition.isCapturingMove(lastChanceCapture.move, Player::two),
        "an existing breakable five is answered with a capture");
    MoveUndo captureUndo;
    reportedCapturePosition.play(lastChanceCapture.move, Player::two, captureUndo);
    expect(!reportedCapturePosition.hasFive(Player::one),
        "the last-chance capture actually breaks the existing five");
}

} // namespace

int main() {
    testCaptureAndUndo();
    testMultipleCapture();
    testDoubleThreeAndCaptureException();
    testWins();
    testIncrementalStateSequence();
    testPatternHeuristic();
    testSearch();
    if (failures != 0) {
        std::cerr << failures << " test(s) failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "All C++ engine tests passed\n";
    return EXIT_SUCCESS;
}
