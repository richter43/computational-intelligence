#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 12:18:04 2021

@author: foxtrot
"""

import GameData as gd
import agents
import game


class Node(object):
    def __init__(self, local_game_state: game.Game, parent=None):
        
        self.parent = parent # Parent node
        self.local_game_state = local_game_state # Player object whose turn is current
        self.score = 0 #Assigned score so far to this node
        self.visits = 0 #Amount of times this node has been visited
        self.branches = [] #Child  branches
        self.leaf = True #Whether or not this is a leaf or does it have children
        self.terminal = False #Whether or not this is a terminal node or not

    def add_branch(self, state):
        node = Node(state, parent=self)
        self.branches.append(node)
        self.leaf = False
        return node
