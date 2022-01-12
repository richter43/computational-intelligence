#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 15:22:39 2021

@author: foxtrot
"""

from typing import List
import numpy as np

import game
import GameData as gd
from .agent_interface import Agent, Action

SerializedGameData = str


class RandomAgent(Agent):

    def __init__(self, name: str):
        super().__init__(name)

    def decide_action(self, data: gd.ServerGameStateData):
        """
        Decides which course of action is best given the state of the game
        """

        action = np.random.choice(Action, 1)[0]
        if action == Action.play:
            request = self.random_play()
        elif action == Action.discard:
            if data.usedNoteTokens > 1:
                request = self.random_discard()
            else:
                return self.decide_action(data)
        else:
            request = self.random_hint(data.players)

        return request

    def random_play(self) -> SerializedGameData:
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

    def random_hint(self, players: List[game.Player]) -> SerializedGameData:
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

    def random_discard(self) -> SerializedGameData:
        """
        Discards a random card

        Returns
        -------
        SerializedGameData
            Serialized request.

        """
        card_idx = np.random.choice(list(range(self.num_cards)), 1)[0]
        
        return super().discard(card_idx)