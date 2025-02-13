#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 15:22:39 2021

@author: foxtrot
"""

import numpy as np

import GameData as gd
from utils import utility
from .agent_interface import Agent

SerializedGameData = str


class DeterministicAgent(Agent):

    def __init__(self, name: str):
        super().__init__(name)

    def decide_action(self, data: gd.ServerGameStateData):

        """
        Decides which course of action is best given the state of the game
        """

        playability_percentages = np.array(
            [utility.playable_percentage(cloud_card, data.tableCards) for cloud_card in self.hand_possible_cards])
        max_playability = np.max(playability_percentages)

        if max_playability > 0.6:
            # Play if possible
            max_idx = np.argmax(playability_percentages)
            request = super().play(max_idx)
        elif data.usedNoteTokens < 8:
            # Hint if possible
            ret_hint = self.player_playable_card(data.players, data.tableCards)

            if ret_hint is None:
                ret_hint = utility.random_hint([server_player for server_player in data.players if server_player.name != self.name])

            player_name, hint_type, hint = ret_hint
            request = super().hint(player_name, hint_type, hint, data.players)
        else:
            least_info_card = utility.least_info_card(self.hand_possible_cards)
            request = super().discard(least_info_card)
        #Discard the card we know the least about

        return request