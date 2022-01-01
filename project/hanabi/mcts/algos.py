#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:27:29 2021

@author: foxtrot
"""

import utils.squilibs as c4
import numpy as np
import utils.tree as t
import utils.mcts as mcts_lib
from collections import Counter
import time

BRANCHING_FACTOR = 7
PLAYER_1 = 1
PLAYER_2 = -1
MAX_DEPTH = 5
MAX_SCORE = 1000


def minmax(board, player, level):
    '''

    Parameters
    ----------
    board : Numpy array
        DESCRIPTION.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.
    level : Integer
        Represents the depth at which the recursion is currently at.

    Returns
    -------
    Integer
        Score.

    '''

    board_moves = c4.valid_moves(board)

    if c4.four_in_a_row(board, 1) or c4.four_in_a_row(board, -1):
        return (None, player*(level+1))
    elif level == 0 or not board_moves:
        return (None, 0)

    ans = (None, -2**32) if player == PLAYER_1 else (None, 2**32)

    for move in board_moves:
        c4.play(board, move, player)
        tmpAns = minmax(board, -player, level - 1)
        c4.take_back(board, move)
        ans = max(ans, (move, -tmpAns[1]), key=lambda x: x[1])

    return ans


def minimax_alphabeta(board, player, level, alpha, beta):
    '''

    Modified version of the minmax which introduces alpha beta pruning

    Parameters
    ----------
    board : Numpy array
        Contains a connect4 state.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.
    level : Integer
        Represents the depth at which the recursion is currently at.

    Returns
    -------
    Tuple (move, score)
        Summary of computation.

    '''

    if c4.four_in_a_row(board, 1) or c4.four_in_a_row(board, -1):
        return (None, player*(level+1))
    elif level == 0 or not c4.valid_moves(board):
        return (None, 0)

    board_moves = c4.valid_moves(board)
    for move in board_moves:
        c4.play(board, move, player)
        tmpAlpha = minimax_alphabeta(
            board, -player, level - 1, (beta[0], -beta[1]), (alpha[0], -alpha[1]))
        c4.take_back(board, move)
        alpha = max(alpha, (move, -tmpAlpha[1]), key=lambda x: x[1])
        if alpha[1] >= beta[1]:
            return beta

    return alpha


def minimax_montecarloeval(board, player, level, alpha, beta):
    '''

    Modified version of the minmax which introduces alpha beta pruning

    Parameters
    ----------
    board : Numpy array
        Contains a connect4 state.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.
    level : Integer
        Represents the depth at which the recursion is currently at.

    Returns
    -------
    Tuple (move, score)
        Summary of computation.

    '''

    if c4.four_in_a_row(board, 1) or c4.four_in_a_row(board, -1):
        # return (None, player*(level+1))
        return (None, player)
    elif not c4.valid_moves(board):
        return (None, 0)
    elif level == 0:
        return (None, player*(c4.montecarlo(board, player)))

    board_moves = c4.valid_moves(board)
    for move in board_moves:
        c4.play(board, move, player)
        tmpAlpha = minimax_montecarloeval(
            board, -player, level - 1, (beta[0], -beta[1]), (alpha[0], -alpha[1]))
        c4.take_back(board, move)
        alpha = max(alpha, (move, -tmpAlpha[1]), key=lambda x: x[1])
        if alpha[1] >= beta[1]:
            return beta

    return alpha


def max_montecarloeval(board, player):
    '''

    Algorithm that maximizes the Monte Carlo evaluation to find the best move

    Parameters
    ----------
    board : Numpy array
        Contains a connect4 state.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.

    Returns
    -------
    None.

    '''

    prob = 0
    while not c4.four_in_a_row(board, player):
        best_move = -1

        for move in c4.valid_moves(board):
            board_copy = board.copy()
            c4.play(board_copy, move, player)
            new_prob = player*c4.montecarlo(board_copy, player)
            if new_prob > prob:
                best_move = move
                prob = new_prob
        c4.play(board, best_move, player)
        print(board)
        moves = c4.valid_moves(board)
        if len(moves) == 0:
            break
        cont_move = np.random.choice(moves, 1)[0]
        c4.play(board, cont_move, -player)


def place_randomly(board, player):
    '''
    Places a piece of the given player in the board

    Parameters
    ----------
    board : Numpy array
        Contains a connect4 state.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.

    Returns
    -------
    None.

    '''
    play = np.random.choice(c4.valid_moves(board), 1)[0]
    c4.play(board, play, player)


def mcts(root, player, max_time):
    '''
    Implementation of the Montecarlo Tree Search that uses time for restricting 
    the computation cycles

    Parameters
    ----------
    root : Tree node
        Node that represents the root.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.
    max_time : Integer
        Time in seconds.

    Returns
    -------
    Integer
        Best move returned as the column number.

    '''

    start_time = time.time()

    while time.time() - start_time < max_time:
        best_node = mcts_lib.select_best(root)
        sim_node = mcts_lib.expand(best_node)
        mcts_lib.simulate(sim_node)
        mcts_lib.backprop(sim_node)

    score_array = [
        b.score/b.visits if not b.terminal else MAX_SCORE for b in root.branches]
    return np.argmax(score_array)


def mcts_ms(root, player, max_time):
    '''
    Implementation of the Montecarlo Tree Search - Modified Selection 
    that uses time for restricting the computation cycles

    This modified version does a simulation using minimax_alphabeta_montecarloeval
    in the selection step, if the simulation checks out it doesn't expand any further

    Parameters
    ----------
    root : Tree node
        Node that represents the root.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.
    max_time : Integer
        Time in seconds.

    Returns
    -------
    Integer
        Best move returned as the column number    

    '''

    start_time = time.time()

    while time.time() - start_time < max_time:
        best_node = mcts_lib.select_best_ms_alphabeta(root)
        if best_node is None:
            continue
        sim_node = mcts_lib.expand(best_node)
        mcts_lib.simulate(sim_node)
        mcts_lib.backprop(sim_node)

    score_array = [
        b.score/b.visits if not b.terminal else MAX_SCORE for b in root.branches]
    return np.argmax(score_array)


def sim(board, player):
    '''
    Iterator that plays sim_amount random games and returns the amount of games
    won by player

    Parameters
    ----------
    board : Numpy array
        Contains a connect4 state.
    player : Integer
        Values are either 1 or -1, the player is the one currently playing.

    Returns
    -------
    Integer
        Amount of wins in the simulation, maximum number is montecarlo_samples.

    '''

    sim_amount = 100
    cnt = Counter(c4._mc(np.copy(board), player)
                  for _ in range(sim_amount))
    return cnt[player]
