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
import game


def handle_startgame_player(
    data: gd.ServerStartGameData, player: agents.Agent, barrier: Barrier, sock: socket.socket
):

    # Number of cards being played, depends on the amount of players
    player.initialize(data.players)

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


def handle_gamestate_player(data: gd.ServerGameStateData, agent: agents.Agent, sock: socket.socket):

    logging.debug(f"Card set size before taking into account player cards: {len(agent.total_possible_cards)}")

    agent.cull_other_player_info(data.players, data.discardPile)

    get_legal_moves(agent.local_game)

    logging.debug(f"Card set size after taking into account player cards: {len(agent.total_possible_cards)}")

    if data.currentPlayer == agent.name:

        agent.update_local_game(data)

        logging.debug(f"Current player: {data.currentPlayer}")
        # request = random_play(name, num_cards)
        request = agent.decide_action(data)
        sock.send(request)

def get_legal_moves(game_state: game.Game):

    player_idx = game_state._Game__currentPlayer
    cur_player = game_state._Game__players[player_idx]

    moves = [(i, j) for i in [agents.Action.play, agents.Action.discard] for j in range(len(cur_player.hand))]

    for index, local_player in enumerate(game_state._Game__players):
        if index != player_idx:
            for card_idx in range(len(local_player.hand)):
                moves.append((agents.Action.hint, (local_player.name, card_idx)))

    return moves





