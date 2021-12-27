#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:46:46 2021

@author: foxtrot
"""
import utils.actions as actions
import numpy as np

import game
import GameData as gd


class Player(object):
    def __init__(self, name: str, play, hint, discard):
        self.name = name
        self.play = play
        self.hint = hint
        self.discard = discard
        self.local_game = game.Game()
        # Keep a local copy of all the possible cards
        self.total_possible_cards = set(self.local_game ._Game__cardsToDraw)
        # Initialized at init_hand()
        self.num_cards = None
        self.hand_possible_cards = None

    def decide_action(self, data: gd.ServerGameStateData) -> str:
        return "Ana karina rote"

    def init_hand(self, num_players: int):
        if num_players < 4:
            self.num_cards = 5
        else:
            self.num_cards = 4
        # Initializing possible cards
        self.hand_possible_cards = [
            self.total_possible_cards for _ in range(self.num_cards)]


class RandomPlayer(Player):

    def __init__(self, name: str):
        super().__init__(name, actions.random_play,
                         actions.random_hint, actions.random_discard)

    def decide_action(self, data: gd.ServerGameStateData):
        val = np.random.rand()
        if val < 1/3:
            request = self.play(self.name, self.num_cards)
        elif val > 2/3:
            if data.usedNoteTokens > 1:
                request = self.discard(self.name, self.hand_possible_cards,
                                       self.total_possible_cards)
            else:
                return self.decide_action(data)
        else:
            request = self.hint(self.name, data.players)

        return request
