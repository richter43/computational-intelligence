#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 00:41:19 2021

@author: foxtrot
"""
import socket
from threading import Barrier
from copy import deepcopy

from typing import List, Set
import logging

import utils.actions as actions
import GameData as gd
import game


def handle_startgame(data: gd.ServerStartGameData, name: str, card_set: Set[game.Card], barrier: Barrier, sock: socket.socket) -> int:
    # Number of cards being played, depends on the amount of players
    if len(data.players) < 4:
        num_cards = 5
    else:
        num_cards = 4
    # Initializing possible cards
    possible_cards = [deepcopy(card_set) for _ in range(num_cards)]
    # %% Ready up / Initializes game
    sock.send(gd.ClientPlayerReadyData(name).serialize())
    logging.debug(f"Sent -> {name} : {gd.ClientPlayerReadyData}")
    barrier.wait()

    sock.send(gd.ClientGetGameStateRequest(name).serialize())
    logging.debug(
        f"Sent -> {name} : {gd.ClientGetGameStateRequest}")

    return num_cards, possible_cards


def handle_hint(data: gd.ServerHintData, possible_cards: List[Set[game.Card]], name: str):

    if data.destination == name:
        if data.type == "value":
            def hint_compare(card: game.Card, data: gd.ServerHintData) -> bool:
                return data.value == card.value
        else:
            def hint_compare(card: game.Card, data: gd.ServerHintData) -> bool:
                return data.value == card.color

        logging.debug(
            f"Player {name} knows {data.type}: {data.value} is at locations {data.positions}")

        for idx in data.positions:
            possible_cards[idx] = set(
                [card for card in possible_cards[idx] if hint_compare(card, data)])


def handle_gamestate(data: gd.ServerGameStateData, card_set: Set[game.Card], name: str, sock: socket.socket):
    for player in data.players:
        card_set -= set(player.hand)

    if data.currentPlayer == name:
        logging.debug(f"Current player: {data.currentPlayer}")
        # request = random_play(name, num_cards)
        request = actions.random_hint(name, data.players)
        sock.send(request)
