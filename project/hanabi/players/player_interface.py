#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:46:46 2021

@author: foxtrot
"""

import game
import GameData as gd
import logging
from copy import deepcopy

SerializedGameData = str


class Player(object):
    def __init__(self, name: str):
        self.name = name
        self.local_game = game.Game()
        # Keep a local copy of all the possible cards
        self.total_possible_cards = set(self.local_game._Game__cardsToDraw)
        # Initialized at init_hand()
        self.num_cards = None
        self.hand_possible_cards = None

    def init_hand(self, num_players: int):
        """

        Initialize the list of all possible cards

        Parameters
        ----------
        num_players : int
            Number of players in the game.

        Returns
        -------
        None.
            All of the variables are created in the class

        """
        if num_players < 4:
            self.num_cards = 5
        else:
            self.num_cards = 4
        # Initializing possible cards
        self.hand_possible_cards = [self.total_possible_cards for _ in range(self.num_cards)]

    def cull_posibilities(self, data: gd.ServerGameStateData):
        if data.type == "value":

            def hint_compare(card: game.Card, data: gd.ServerHintData) -> bool:
                return int(data.value) == card.value

        else:

            def hint_compare(card: game.Card, data: gd.ServerHintData) -> bool:
                return data.value == card.color

        logging.info(f"Player {self.name} knows {data.type}: {data.value} is at locations {data.positions}")

        logging.info(
            f"Possibilites before hint: {sum([len(self.hand_possible_cards[idx]) for idx in range(self.num_cards)])}"
        )

        for idx in range(self.num_cards):
            casted_positions = [int(i) for i in data.positions]
            if idx in casted_positions:
                self.hand_possible_cards[idx] = set(
                    [card for card in self.hand_possible_cards[idx] if hint_compare(card, data)]
                )
            else:
                self.hand_possible_cards[idx] = set(
                    [card for card in self.hand_possible_cards[idx] if not hint_compare(card, data)]
                )

        logging.info(
            f"Possibilites after hint: {sum([len(self.hand_possible_cards[idx]) for idx in range(self.num_cards)])}"
        )

    def decide_action(self, data: gd.ServerGameStateData) -> str:
        pass

    def play(self, play: int) -> SerializedGameData:
        logging.info(f"{self.name} played {play}")
        request = gd.ClientPlayerPlayCardRequest(self.name, play).serialize()
        return request

    def hint(self, hinted_player_name: str, hint_type: str, hint_value: str) -> SerializedGameData:
        
        request = gd.ClientHintData(self.name, hinted_player_name, hint_type, hint_value).serialize()
        logging.info(f"{self.name} hinted {hint_type}: {hint_value}")

        return request
    
    def discard(self, card_idx: int) -> SerializedGameData:
        self.hand_possible_cards[card_idx] = deepcopy(self.total_possible_cards)
        logging.info(f"{self.name} discarded {card_idx}")
        request = gd.ClientPlayerDiscardCardRequest(self.name, card_idx).serialize()
        return request
