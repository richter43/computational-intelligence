#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:46:46 2021

@author: foxtrot
"""
from typing import List, Set
import logging
import utils.actions as actions
import numpy as np
from copy import deepcopy

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


class RandomPlayer(Player):

    def __init__(self, name: str):
        super().__init__(name)

    def decide_action(self, data: gd.ServerGameStateData):
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

    def play(self) -> SerializedGameData:
        """
        Return a random play

        Returns
        -------
        SerializedGameData
            Serialized request.

        """
        plays = list(range(self.num_cards))
        play = int(np.random.choice(plays, 1)[0])
        logging.debug(f"{self.name} played {play}")
        request = gd.ClientPlayerPlayCardRequest(self.name, play).serialize()
        return request

    def hint(self, players: List[game.Player]) -> SerializedGameData:
        """
        Return a random hint

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

        request = gd.ClientHintData(self.name, player.name, sel_type, value).serialize()

        return request

    def discard(self) -> SerializedGameData:
        """
        Discard a random card

        Returns
        -------
        SerializedGameData
            Serialized request.

        """
        card_idx = np.random.choice(list(range(self.num_cards)), 1)[0]
        logging.debug(f"{self.name} discarded {card_idx}")
        self.hand_possible_cards[card_idx] = deepcopy(self.total_possible_cards)
        request = gd.ClientPlayerDiscardCardRequest(self.name, card_idx).serialize()
        return request
