#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 15:22:39 2021

@author: foxtrot
"""

from typing import List
import logging
import numpy as np
from copy import deepcopy


import game
import GameData as gd
from .agent_interface import Agent

SerializedGameData = str


class DeterministicAgent(Agent):

    def __init__(self, name: str):
        super().__init__(name)

    def decide_action(self, data: gd.ServerGameStateData):
        """
        Decides which course of action is best given the state of the game
        """
        val = np.random.rand()
        if val < 1/3:
            request = self.play()
        elif val > 2/3:
            if data.usedNoteTokens > 1:
                request = self.discard()
            else:
                return self.decide_action(data)
        else:
            request = self.hint(data.players)

        return request

    def deterministic_play(self) -> SerializedGameData:
        """
        Returns a random play

        Returns
        -------
        SerializedGameData
            Serialized request.

        """
        plays = list(range(self.num_cards))
        card_pos = int(np.random.choice(plays, 1)[0])
        return super().play(card_pos)

    def deterministic_hint(self, players: List[game.Player]) -> SerializedGameData:
        """
        Returns a random hint

        players : List[game.Player]
            List of the other players (Contains cards and all).

        Returns
        -------
        SerializedGameData
            Serialized request.

        """

        types = ["value", "color"]

        player = np.random.choice(players, 1)[0]
        card = np.random.choice(player.hand, 1)[0]
        sel_type = np.random.choice(types, 1)[0]

        if sel_type == "value":
            value = card.value
        else:
            value = card.color

        return super().hint(player.name, sel_type, value)

    def deterministic_discard(self) -> SerializedGameData:
        """
        Discards a random card

        Returns
        -------
        SerializedGameData
            Serialized request.

        """
        card_idx = np.random.choice(list(range(self.num_cards)), 1)[0]
        
        return super().discard(card_idx)
