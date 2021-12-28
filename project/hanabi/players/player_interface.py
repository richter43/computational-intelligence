#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:46:46 2021

@author: foxtrot
"""

import game
import GameData as gd

SerializedGameData = str


class Player(object):
    def __init__(self, name: str):
        self.name = name
        self.local_game = game.Game()
        # Keep a local copy of all the possible cards
        self.total_possible_cards = set(self.local_game ._Game__cardsToDraw)
        # Initialized at init_hand()
        self.num_cards = None
        self.hand_possible_cards = None

    def init_hand(self, num_players: int):
        if num_players < 4:
            self.num_cards = 5
        else:
            self.num_cards = 4
        # Initializing possible cards
        self.hand_possible_cards = [
            self.total_possible_cards for _ in range(self.num_cards)]

    def decide_action(self, data: gd.ServerGameStateData) -> str:
        pass

    def play(self):
        pass

    def hint(self):
        pass

    def discard(self):
        pass
