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
from enum import Enum, auto
from typing import Tuple, List

SerializedGameData = str

class Action(Enum):
    play = auto()
    hint = auto()
    discard = auto()

class Agent(object):
    def __init__(self, name: str, determinized=False, cards=None):
        self.name = name
        self.local_game = game.Game()
        # Keep a local copy of all the possible cards
        self.total_possible_cards = set(self.local_game._Game__cardsToDraw)
        # Initialized at init_hand()
        self.num_cards = None
        self.hand_possible_cards = cards
        # self.determinized = determinized

    def initialize(self, list_player: List[str]):

        self.num_players = len(list_player)

        if self.num_players < 4:
            self.num_cards = 5
        else:
            self.num_cards = 4

        self.init_local_game(list_player)
        self.init_hand()

        
    def init_hand(self):
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
        # Initializing possible cards
        self.hand_possible_cards = [deepcopy(self.total_possible_cards) for _ in range(self.num_cards)]


    def init_local_game(self, list_player: List[str]):
        
        self.local_game._Game__cardsToDraw = [None for i in range(len(self.total_possible_cards) - self.num_players * self.num_cards)] # Set possible cards to None since they are unknown
        logging.debug(f"local_game cards to draw is set to {self.local_game._Game__cardsToDraw[0]} for {len(self.local_game._Game__cardsToDraw)} cards.")
        
        #Adding players to the locally instantiated game
        for player_name in list_player:
            self.local_game.addPlayer(player_name)
            

    def cull_other_player_info(self, player_list: List[game.Player], discard_pile: List[game.Card]):
        
        for other_player in player_list:
            del_set = set(other_player.hand) | set(discard_pile)
            self.total_possible_cards -= del_set
            self.hand_possible_cards = [self.total_possible_cards - del_set for card_set in self.hand_possible_cards]
        

    def cull_posibilities(self, data: gd.ServerHintData):
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
    
    # def get_moves(self):
    #
    #     moves = [(i, j) for i in [Action.play, Action.discard] for j in range(self.num_cards)]
    #
    #     for local_player in self.local_game._Game__player:
    #         if local_player.name != self.name:
    #             for card_idx in range(len(local_player.hand)):
    #                 moves.append((Action.hint, card_idx))
    #
    #     return moves
    
    def decide_action(self, data: gd.ServerGameStateData) -> str:
        pass

    def update_local_game(self, data: gd.ServerGameStateData):

        """
        Updates local game's state
        """

        self.local_game._Game__tableCards = deepcopy(data.tableCards)
        self.local_game._Game__usedNoteTokens = deepcopy(data.usedNoteTokens)
        self.local_game._Game__usedStormTokens = deepcopy(data.usedStormTokens)
        self.local_game._Game__discardPile = deepcopy(data.discardPile)

        for index, local_player in enumerate(self.local_game._Game__players):

            if local_player.name == data.currentPlayer:
                self.local_game._Game__currentPlayer = index
                local_player.hand = self.hand_possible_cards
                continue

            for server_player in data.players:
                if local_player.name == server_player.name:
                    # Update the non-agent player's hand with their actual hand
                    local_player.hand = deepcopy(server_player.hand)
                    break
