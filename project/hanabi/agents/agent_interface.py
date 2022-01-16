#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:46:46 2021

@author: foxtrot
"""

from enum import Enum, auto
import logging
from typing import List, Tuple, Dict
from copy import deepcopy
from utils import utility
import numpy as np

import game
import GameData as gd



SerializedGameData = str

class Action(Enum):
    play = auto()
    hint = auto()
    discard = auto()

class Agent(object):
    def __init__(self, name: str):
        self.name = name
        self.local_game = game.Game()
        # Keep a local copy of all the possible cards
        self.total_possible_cards = set(self.local_game._Game__cardsToDraw)
        # Initialized at init_hand()
        self.num_cards = None
        self.hand_possible_cards = None
        self.list_given_hint = {} #Dictionary of List of the given hints

    def init_hand(self, server_players: List[game.Player]):
        """

        Initialize the list of all possible cards

        Parameters
        ----------
        num_players : int
            Number of agents in the game.

        Returns
        -------
        None.
            All the variables are created in the class

        """
        num_players = len(server_players)

        if num_players < 4:
            self.num_cards = 5
        else:
            self.num_cards = 4
        # Initializing possible cards

        for player in server_players:
            self.list_given_hint[player] = [ set() for _ in range(self.num_cards)]

        self.hand_possible_cards = [self.total_possible_cards for _ in range(self.num_cards)]

    def cull_possibilities(self, data: gd.ServerHintData):
        """
        Remove from the pool of possible cards the hinted card

        Args:
            data: Hint data packet

        """
        if data.type == "value":
            # Creating a function that extracts the info from the received data depending on the passed hint,
            # It was created as a function instead of a lambda-function in order to follow PEP8
            def hint_compare(card: game.Card, inner_data: gd.ServerHintData) -> bool:
                return int(inner_data.value) == card.value

        else:

            def hint_compare(card: game.Card, inner_data: gd.ServerHintData) -> bool:
                return inner_data.value == card.color

        logging.info(f"Player {self.name} knows {data.type}: {data.value} is at locations {data.positions}")

        logging.debug(
            f"Possibilites before hint: {sum([len(self.hand_possible_cards[idx]) for idx in range(self.num_cards)])}"
        )

        for idx in range(self.num_cards):
            casted_positions = [int(i) for i in data.positions]
            if idx in casted_positions:
                tmp = set(
                    [card for card in self.hand_possible_cards[idx] if hint_compare(card, data)]
                )

                # if len(tmp) == 0:
                #     breakpoint()

                self.hand_possible_cards[idx] = tmp
            else:
                tmp = set(
                    [card for card in self.hand_possible_cards[idx] if not hint_compare(card, data)]
                )

                # if len(tmp) == 0:
                #     breakpoint()

                self.hand_possible_cards[idx] = tmp

        logging.debug(
            f"Possibilites after hint: {sum([len(self.hand_possible_cards[idx]) for idx in range(self.num_cards)])}"
        )

    def decide_action(self, data: gd.ServerGameStateData) -> str:
        """
        Method that should be implemented at every child class

        Args:
            data:
        """
        pass

    def play(self, card_idx: int) -> SerializedGameData:
        """

        Creates a serialized play request

        Args:
            card_idx: position of the card to be played

        Returns:
            Serialized object to be sent
        """
        # breakpoint()

        logging.info(f"{self.name} played {card_idx}")
        request = gd.ClientPlayerPlayCardRequest(self.name, card_idx).serialize()
        del self.hand_possible_cards[card_idx]
        self.hand_possible_cards.append(deepcopy(self.total_possible_cards))
        return request

    def hint(self, hinted_player_name: str, hint_type: str, hint_value: str, player_list: List[game.Player] = None) -> SerializedGameData:
        """

        Creates a serialized hint request

        Args:
            hinted_player_name: Name of the player that's getting the hint
            hint_type: self-explanatory
            hint_value: self-explanatory
            player_list: self-explanatory

        Returns:
            Serialized object to be sent
        """
        if player_list is not None:
            self.append_given_hint((hinted_player_name, hint_type, hint_value), player_list)

        request = gd.ClientHintData(self.name, hinted_player_name, hint_type, hint_value).serialize()
        logging.info(f"{self.name} hinted {hint_type}: {hint_value}")

        return request
    
    def discard(self, card_idx: int) -> SerializedGameData:
        """

        Creates a serialized discard request

        Args:
            card_idx: position of the card to be discarded

        Returns:

        """
        del self.hand_possible_cards[card_idx]
        self.hand_possible_cards.append(deepcopy(self.total_possible_cards))
        logging.info(f"{self.name} discarded {card_idx}")
        request = gd.ClientPlayerDiscardCardRequest(self.name, card_idx).serialize()
        return request

    def append_given_hint(self, hint: Tuple[str, str, object], server_player_list: List[game.Player]):
        """

        Add that the hint was already given

        Args:
            hint: self-explanatory
            server_player_list: List of players passed by the server
        """
        hinted_player, hint_type, hint_value = hint

        if hint_type == "value":
            def compare_value(card: game.Card, value: int):
                return card.value == value
        else:
            def compare_value(card: game.Card, value: str):
                return card.color == value

        for player in server_player_list:
            if player.name == hinted_player:
                for idx, card in enumerate(player.hand):
                    if compare_value(card, hint_value):
                        self.list_given_hint[hinted_player][idx].add((hint_type, hint_value))
            break

    def player_playable_card(self, player_list: List[game.Player], table_state: Dict[str, List[int]]) -> Tuple[
        str, str, object]:
        """

        Choose which hint is better depending on the playability of the card

        Args:
            player_list: List of players passed by the server
            table_state: current state of the table

        Returns:
            Possible hint
        """
        pos_cards = set()

        for server_player in player_list:
            for card_idx, card  in enumerate(server_player.hand):
                if utility.playable(card, table_state):
                    if not self.hinted_color(card, card_idx, server_player.name):
                        pos_cards.add((server_player.name, "color", card.color))
                    if not self.hinted_value(card, card_idx, server_player.name):
                        pos_cards.add((server_player.name, "value", card.value))

        if len(pos_cards) == 0:
            return None

        list_pos_cards = list(pos_cards)
        card_idx = np.random.choice(len(list_pos_cards), 1)[0]

        return list_pos_cards[card_idx]

    def hinted_color(self, card: game.Card, card_idx: int, player_name: str) -> bool:
        """

        Check if color has already been hinted

        Args:
            card: given card
            card_idx: card position
            player_name: name of the player to be hinted

        """
        return ("color", card.color) in self.list_given_hint[player_name][card_idx]

    def hinted_value(self, card: game.Card, card_idx: int, player_name: str) -> bool:
        """

        Check if value has already been hinted

        Args:
            card: given card
            card_idx: card position
            player_name: name of the player to be hinted

        """
        return ("value", card.value) in self.list_given_hint[player_name][card_idx]

    def cull_visible_cards(self, data: gd.ServerGameStateData):
        """

        Remove the cards from the set of unseen cards (Deck)

        Args:
            data: Packet passed info
        """
        logging.debug(f"Card set size before taking into account player cards: {len(self.total_possible_cards)}")

        for other_player in data.players:
            del_set = set(other_player.hand) | set(data.discardPile)
            self.total_possible_cards -= del_set
            self.hand_possible_cards = [card_set - del_set for card_set in self.hand_possible_cards]

        logging.debug(f"Card set size after taking into account player cards: {len(self.total_possible_cards)}")

    def reset_total_cards(self):
        """
        Resets the deck
        """
        self.total_possible_cards = set(self.local_game._Game__cardsToDraw)