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
    players: List[game.Player], agent: Agent, barrier: Barrier, sock: socket.socket
):
    """
    Handles a game start situation

    Args:
        players: List of server players
        agent: self-explanatory
        barrier: barrier that simulates the waiting of other agents getting readied
        sock: socket through which the packets are sent
    """
    # Number of cards being played, depends on the amount of agents
    agent.reset_total_cards()
    agent.init_hand(players)

    # %% Ready up / Initializes game
    sock.send(gd.ClientPlayerReadyData(agent.name).serialize())
    logging.debug(f"Sent -> {agent.name} : {gd.ClientPlayerReadyData}")

    barrier.wait()

    sock.send(gd.ClientGetGameStateRequest(agent.name).serialize())
    logging.debug(f"Sent -> {agent.name} : {gd.ClientGetGameStateRequest}")


def handle_hint_player(data: gd.ServerHintData, agent: Agent):
    """
    Handles a hint
    Args:
        data: hint packet
        agent: self-explanatory
    """
    if data.destination == agent.name:
        agent.cull_possibilities(data)
    else:
        agent.append_other_player_given_hint(data)


def handle_gamestate_player(data: gd.ServerGameStateData, agent: Agent, sock: socket.socket):
    """
    Handles a turn
    Args:
        data: packet that relays the state of the game
        agent: self-explanatory
        sock: socket through which the packets are sent
    """
    logging.debug(f"Current player: {data.currentPlayer}")
    # request = random_play(name, num_cards)
    request = agent.decide_action(data)
    sock.send(request)