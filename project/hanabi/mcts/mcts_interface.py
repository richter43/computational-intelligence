#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:58:31 2022
@author: foxtrot
"""

from time import time
import numpy as np

from copy import deepcopy

from agents import Action
import utils.handlers as handlers
from .tree import Node


class MCTS(object):
    """
    Implementation of MCTS with perfect information

    Using MCTS to give the best hint
    Simulate the player playing that card with the current state of the board
    Compute how good it is by showing how many times would it be a good move
    Done
    """

    def __init__(self, rootnode: Node, max_time: time):

        self.rootnode = rootnode
        self.max_time = max_time

        return

    def select(self, node: Node, C=1):
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

        score_array = np.array(
            [self.ucb(b.score, node.visits, b.visits, C) if not b.terminal else -1 for b in node.branches])

        idx = np.argmax(score_array)

        return self.select(node.branches[idx])

    def expand(self, node: Node) -> Node:
        """
        Expansion step of the Monte Carlo Tree Search
        Parameters
        ----------
        node : Tree Node
            Node that contains information about the current state.
        Returns
        -------
        Tree Node
            Node for simulation.
        """

        game_state = deepcopy(node.local_game_state)
        node.leaf = False

        val_moves = handlers.get_legal_moves(game_state)

        if len(val_moves) == 0:
            return None

        tmpList = []

        for action, content in val_moves:

            if action == Action.play:

            elif action == Action.hint:

            elif action == Action.discard:


            gane_state._Game__nextTurn()

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

    def simulate():
        pass

    def backpropagate():
        pass

    def run(self):

        start_time = time.time()

        while time.time() - start_time < self.max_time:
            best_node = self.select()
            sim_node = self.expand()
            self.simulate()
            self.backpropagate()

        score_array = [
            b.score / b.visits if not b.terminal else MAX_SCORE for b in root.branches]
        return np.argmax(score_array)

    def ucb(score, par_n, n, C):
        return score / n + C * np.sqrt(2 * np.log(par_n) / n)