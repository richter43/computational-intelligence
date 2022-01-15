#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 00:41:19 2021

@author: foxtrot
"""
import socket
from threading import Barrier
import logging
from typing import List

import game
from agents import Agent
import GameData as gd


def handle_startgame_player(
    players: List[game.Player], player: Agent, barrier: Barrier, sock: socket.socket
):

    # Number of cards being played, depends on the amount of agents
    player.reset_total_cards()
    player.init_hand(players)

    # %% Ready up / Initializes game
    sock.send(gd.ClientPlayerReadyData(player.name).serialize())
    logging.debug(f"Sent -> {player.name} : {gd.ClientPlayerReadyData}")

    barrier.wait()

    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())
    logging.debug(f"Sent -> {player.name} : {gd.ClientGetGameStateRequest}")


def handle_hint_player(data: gd.ServerHintData, player: Agent):

    # TODO: Also modelling what the others know about their own cards

    if data.destination == player.name:
        player.cull_posibilities(data)


def handle_gamestate_player(data: gd.ServerGameStateData, player: Agent, sock: socket.socket):

    logging.debug(f"Current player: {data.currentPlayer}")
    # request = random_play(name, num_cards)
    request = player.decide_action(data)
    sock.send(request)
