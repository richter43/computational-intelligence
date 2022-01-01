#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 14:45:12 2021

@author: foxtrot
"""

import squilibs as c4
import algos
import tree
import numpy as np


def select_best(node: tree.Node, C=1):
    """
    Regular Monte Carlo selection algorithm

    Parameters
    ----------
    node : Tree Node
        Node that contains information about the state.
    C : Integer, optional
        Scaling factor for the UCB equation. The default is 1.

    Returns
    -------
    Tree Node
        Best node according to UCB.

    """

    if node.leaf:
        return node

    visit_array = np.array([b.visits == 0 and not b.terminal for b in node.branches])

    if any(visit_array):
        idx = np.argmax(visit_array)
        return node.branches[idx]

    score_array = np.array([ucb(b.score, node.visits, b.visits, C) if not b.terminal else -1 for b in node.branches])

    idx = np.argmax(score_array)

    return select_best(node.branches[idx])


def select_best_ms_alphabeta(node, C=1):
    """

    Modified Monte Carlo selection algorithm

    Parameters
    ----------
        node : Tree Node
            Node that contains information about the current state.
        C : Integer, optional
            Scaling factor for the UCB equation. The default is 1.

    Returns
    -------
        Tree Node
            Best node according to UCB.

    """

    if node.leaf:
        return node

    visit_array = np.array([b.visits == 0 and not b.terminal for b in node.branches])

    if any(visit_array):
        idx = np.argmax(visit_array)
        return node.branches[idx]

    score_array = np.array([ucb(b.score, node.visits, b.visits, C) if not b.terminal else -1 for b in node.branches])

    idx = np.argmax(score_array)

    tmpNode = node.branches[idx]

    if tmpNode.visits == 1:
        _, tmpScore = algos.minimax_montecarloeval(tmpNode.state, -tmpNode.player, 2, (None, -1000), (None, 1000))

        tmpScore *= 100

        if tmpScore >= tmpNode.score:
            tmpNode.visits += 1
            tmpNode.score += tmpScore
            backprop(tmpNode)
            return None

    return select_best(tmpNode)


def expand(node):
    """
    Expansion algorithm of the Monte Carlo Tree Search

    Parameters
    ----------
    node : Tree Node
        Node that contains information about the current state.

    Returns
    -------
    Tree Node
        Node for simulation.

    """

    board = node.state
    node.leaf = False

    val_moves = c4.valid_moves(board)

    if len(val_moves) == 0:
        return None

    tmpList = []

    for move in val_moves:
        board_copy = board.copy()
        c4.play(board_copy, move, -node.player)
        tmpNode = tree.Node(board_copy, -node.player, node)

        if c4.four_in_a_row(board_copy, -node.player):
            tmpNode.terminal = True
        tmpList.append(tmpNode)

    if c4.four_in_a_row(board, node.player):
        return node

    node.branches = tmpList

    choice = np.random.choice(tmpList, 1)[0]

    return choice


def simulate(node):
    """
    Simulation algorithm of the Monte Carlo Tree Search

    Parameters
    ----------
    node : Tree Node
        Node that contains information about the current state..

    Returns
    -------
    None.

    """

    node.score = algos.sim(node.state.copy(), node.player)
    node.visits += 1

    return


def backprop(node):
    """
    Backpropagation algorithm of the Monte Carlo Tree Search

    Parameters
    ----------
    node : Tree Node
        Node that contains information about the current state..

    Returns
    -------
    None.

    """

    trav_node = node
    while True:
        trav_node = trav_node.parent
        scores = [i.score for i in trav_node.branches]
        trav_node.score = np.sum(scores)
        trav_node.visits += 1
        if trav_node.parent is None:
            break


def ucb(score, par_n, n, C):
    return score / n + C * np.sqrt(2 * np.log(par_n) / n)
