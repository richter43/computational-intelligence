#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 15:22:39 2021

@author: foxtrot
"""

import numpy as np
import numpy.typing as npt

import GameData as gd
from utils import utility
from .agent_interface import Agent

SerializedGameData = str


class GAAgent(Agent):

    def __init__(self, name: str):

        super().__init__(name)

    def decide_action(self, data: gd.ServerGameStateData):

        """
        Decides which course of action is best given the state of the game
        """

        playability_percentages = np.array(
            [utility.playable_percentage(cloud_card, data.tableCards) for cloud_card in self.hand_possible_cards])
        max_playability = np.max(playability_percentages)

        if  max_playability > self.fenotype["max_playability"]:
            # Play if possible
            max_idx = np.argmax(playability_percentages)
            request = super().play(max_idx)
        elif data.usedNoteTokens < 8:
            # Hint if possible

            hint_random = 0.5

            if hint_random < self.fenotype["random_hint"]:
                ret_hint = self.player_playable_card(data.players, data.tableCards)

            if hint_random > self.fenotype["random_hint"] or ret_hint is None:
                ret_hint = utility.random_hint([server_player for server_player in data.players if server_player.name != self.name])

            player_name, hint_type, hint = ret_hint
            request = super().hint(player_name, hint_type, hint, data.players)
        else:

            discard_random = 0.5

            if discard_random <  self.fenotype["random_discard"]:
                discard_card = utility.least_info_card(self.hand_possible_cards)
            else:
                discard_card = utility.choose_random_card(self.num_cards)

            request = super().discard(discard_card)
        #Discard the card we know the least about

        return request

    def set_chromosome(self, chromosome: npt.NDArray[np.float32]):

        self.chromosome = chromosome
        self.fenotype = {"max_playability": self.chromosome[0], "random_hint": self.chromosome[1], "random_discard": self.chromosome[2]}