#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 00:46:23 2021

@author: foxtrot
"""

import numpy as np
import logging
from typing import List, Set
from copy import deepcopy

import game
import GameData as gd

# %% Type hint variables

SerializedGameData = str


def random_play(name: str, num_cards: int) -> SerializedGameData:
    """
    Given the name of a player return a serialized ClientPlayerPlayCardRequest
    """
    plays = list(range(num_cards))
    play = int(np.random.choice(plays, 1)[0])
    logging.debug(f"{name} played {play}")
    request = gd.ClientPlayerPlayCardRequest(name, play).serialize()
    return request


def random_hint(name: str, players: List[game.Player]) -> SerializedGameData:
    """
    Return a random hint

    Parameters
    ----------
    name : str
        Name of the current player.
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

    request = gd.ClientHintData(name, player.name, sel_type, value).serialize()

    return request


def random_discard(name: str, own_cards: List[Set[game.Card]], possible_cards: Set[game.Card]) -> SerializedGameData:

    num_cards = len(own_cards)
    card_idx = np.random.choice(list(range(num_cards)), 1)[0]
    logging.debug(f"{name} discarded {card_idx}")
    own_cards[card_idx] = deepcopy(possible_cards)
    request = gd.ClientPlayerDiscardCardRequest(name, card_idx).serialize()
    return request
