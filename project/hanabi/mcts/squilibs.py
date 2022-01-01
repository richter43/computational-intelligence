#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright **`(c)`** 2021 Giovanni Squillero `<squillero@polito.it>`  
[`https://github.com/squillero/computational-intelligence`](https://github.com/squillero/computational-intelligence)  
Free for personal or classroom use; see 'LICENCE.md' for details.
"""

import numpy as np
from collections import Counter

NUM_COLUMNS = 7
COLUMN_HEIGHT = 6
FOUR = 4

# Board can be initiatilized with `board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)`
# Notez Bien: Connect 4 "columns" are actually NumPy "rows"


def valid_moves(board):
    """Returns columns where a disc may be played"""
    return [n for n in range(NUM_COLUMNS) if board[n, COLUMN_HEIGHT - 1] == 0]


def play(board, column, player):
    """Updates `board` as `player` drops a disc in `column`"""
    (index,) = next((i for i, v in np.ndenumerate(board[column]) if v == 0))
    board[column, index] = player


def take_back(board, column):
    """Updates `board` removing top disc from `column`"""
    (index,) = [i for i, v in np.ndenumerate(board[column]) if v != 0][-1]
    board[column, index] = 0


def four_in_a_row(board, player):
    """Checks if `player` has a 4-piece line"""
    return (
        any(
            all(board[c, r] == player)
            for c in range(NUM_COLUMNS)
            for r in (list(range(n, n + FOUR)) for n in range(COLUMN_HEIGHT - FOUR + 1))
        )
        or any(
            all(board[c, r] == player)
            for r in range(COLUMN_HEIGHT)
            for c in (list(range(n, n + FOUR)) for n in range(NUM_COLUMNS - FOUR + 1))
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co, co + FOUR))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
    )


def _mc(board, player):
    p = -player
    while valid_moves(board):
        p = -p
        c = np.random.choice(valid_moves(board))
        play(board, c, p)
        if four_in_a_row(board, p):
            return p
    return 0


def montecarlo(board, player):
    montecarlo_samples = 100
    cnt = Counter(_mc(np.copy(board), player)
                  for _ in range(montecarlo_samples))
    return (cnt[1] - cnt[-1]) / montecarlo_samples
