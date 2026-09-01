#ifndef GOMOKU_C_API_H
#define GOMOKU_C_API_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct GomokuSearchResult {
    int row;
    int col;
    int score;
    int completed_depth;
    uint64_t nodes;
    uint64_t elapsed_us;
    int status;
} GomokuSearchResult;

enum GomokuStatus {
    GOMOKU_OK = 0,
    GOMOKU_INVALID_ARGUMENT = 1,
    GOMOKU_NO_LEGAL_MOVE = 2,
    GOMOKU_OUT_OF_MEMORY = 3,
    GOMOKU_INTERNAL_ERROR = 4
};

void *gomoku_engine_create(void);
void gomoku_engine_destroy(void *engine);

int gomoku_find_best_move(
    void *engine,
    const uint8_t *cells,
    int cell_count,
    int player,
    int player1_captures,
    int player2_captures,
    int budget_ms,
    GomokuSearchResult *result
);

#ifdef __cplusplus
}
#endif

#endif
