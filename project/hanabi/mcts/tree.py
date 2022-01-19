#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 12:18:04 2021

@author: foxtrot
"""


class Node(object):
    def __init__(self, state, player, parent=None):
        self.parent = parent
        self.player = player
        self.state = state
        self.score = 0
        self.visits = 0
        self.branches = []
        self.leaf = True
        self.terminal = False

    def add_branch(self, state):
        node = Node(state, -self.player, parent=self)
        self.branches.append(node)
        self.leaf = False
        return node
