#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:58:31 2022

@author: foxtrot
"""

from time import time
from players import Action

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
    
    def select():
        pass
    
    def expand(self, node: Node):
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

        table = node.game_state.tableCards
        node.leaf = False

        val_moves = node.player.get_moves()

        if len(val_moves) == 0:
            return None

        tmpList = []

        for action, card_idx in val_moves:
            
            table_copy = table.copy()
            
            if action == Action.play:
                
            elif action == Action.hint:
                
            elif action == Action.discard:
                
            
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
            # best_node = mcts_lib.select_best(root)
            # sim_node = mcts_lib.expand(best_node)
            # mcts_lib.simulate(sim_node)
            # mcts_lib.backprop(sim_node)

        score_array = [
            b.score/b.visits if not b.terminal else MAX_SCORE for b in root.branches]
        return np.argmax(score_array)