#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 00:41:19 2021

@author: foxtrot
"""
import socket
from threading import Barrier
import logging

import agents
import GameData as gd


def handle_startgame_player(
    data: gd.ServerStartGameData, player: agents.Agent, barrier: Barrier, sock: socket.socket
):

    # Number of cards being played, depends on the amount of agents
    player.init_hand(len(data.players))

    # %% Ready up / Initializes game
    sock.send(gd.ClientPlayerReadyData(player.name).serialize())
    logging.debug(f"Sent -> {player.name} : {gd.ClientPlayerReadyData}")
    barrier.wait()

    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())
    logging.debug(f"Sent -> {player.name} : {gd.ClientGetGameStateRequest}")


def handle_hint_player(data: gd.ServerHintData, player: agents.Agent):

    # TODO: Also modelling what the others know about their own cards

    if data.destination == player.name:
        player.cull_posibilities(data)


def handle_gamestate_player(data: gd.ServerGameStateData, player: agents.Agent, sock: socket.socket):

    logging.debug(f"Card set size before taking into account player cards: {len(player.total_possible_cards)}")

    # Remove the other agents' cards from the possibility set
    for other_player in data.players:
        del_set = set(other_player.hand) | set(data.discardPile)
        player.total_possible_cards -= del_set
        player.hand_possible_cards = [player.total_possible_cards - del_set for card_set in player.hand_possible_cards]

    logging.debug(f"Card set size after taking into account player cards: {len(player.total_possible_cards)}")

    if data.currentPlayer == player.name:

        logging.debug(f"Current player: {data.currentPlayer}")
        # request = random_play(name, num_cards)
        request = player.decide_action(data)
        sock.send(request)
