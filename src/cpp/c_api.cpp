#include "gomoku/c_api.h"
#include "gomoku/engine.hpp"

#include <new>

using gomoku::Board;
using gomoku::Engine;
using gomoku::Player;

extern "C" void *gomoku_engine_create(void) {
    try {
        return new Engine();
    } catch (...) {
        return nullptr;
    }
}

extern "C" void gomoku_engine_destroy(void *engine) {
    delete static_cast<Engine *>(engine);
}

extern "C" int gomoku_find_best_move(
    void *engine,
    const uint8_t *cells,
    int cell_count,
    int player,
    int player1_captures,
    int player2_captures,
    int budget_ms,
    GomokuSearchResult *result
) {
    if (result != nullptr) {
        *result = GomokuSearchResult{-1, -1, 0, 0, 0, 0, GOMOKU_INVALID_ARGUMENT};
    }
    if (engine == nullptr || cells == nullptr || result == nullptr || cell_count != gomoku::CellCount
        || (player != 1 && player != 2) || player1_captures < 0 || player2_captures < 0
        || player1_captures > 10 || player2_captures > 10 || budget_ms <= 0) {
        return GOMOKU_INVALID_ARGUMENT;
    }
    try {
        Board board(cells, player1_captures, player2_captures);
        const auto search = static_cast<Engine *>(engine)->findBestMove(
            board, static_cast<Player>(player), budget_ms
        );
        if (!search.move.valid()) {
            result->status = GOMOKU_NO_LEGAL_MOVE;
            return GOMOKU_NO_LEGAL_MOVE;
        }
        *result = GomokuSearchResult{
            search.move.row(), search.move.col(), search.score, search.completedDepth,
            search.nodes, search.elapsedMicroseconds, GOMOKU_OK
        };
        return GOMOKU_OK;
    } catch (const std::bad_alloc &) {
        result->status = GOMOKU_OUT_OF_MEMORY;
        return GOMOKU_OUT_OF_MEMORY;
    } catch (...) {
        result->status = GOMOKU_INTERNAL_ERROR;
        return GOMOKU_INTERNAL_ERROR;
    }
}
