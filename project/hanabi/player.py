#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 19:01:33 2021

@author: foxtrot
"""
import logging
import socket
import sys
import time
from argparse import Namespace
from threading import Thread, Barrier, Lock
from typing import List, Optional

import numpy as np
import numpy.typing as npt

import GameData as gd
import agents
import constants
import utils.handlers as handlers
import utils.localparse as parse
import utils.utility as utility

# %% Global variables
names = ["Richard", "Rasmus", "Tony", "Aubrey", "Don Juan", "Graham", "Dennis", "Jones"]

barrier = None
mutex = None
first = False

barrier_turn_start = None
barrier_turn_end = None


def get_name() -> str:
    """
    Takes, removes and returns a name from the list.
    This code is thread-safe.

    Returns:
        name in a string format
    """
    global names
    global mutex

    mutex.acquire()
    name = np.random.choice(names, 1)[0]
    # Casting to regular string due to numpy being weird and having its own string type ????
    name = str(name)
    names.remove(name)
    mutex.release()

    return name


def player_thread(tid: int, ret: List[int], player_type: str, iterations: int, chromosomes: List[npt.NDArray[np.float32]]=None, slowmode=None) -> None:
    """
    Code which will run the agent/player
    Args:
        tid: Thread ID (Used for debugging purposes)
        ret: List in which the scores will be returned
        player_type: Type of agent that will be instantiated
        iterations: Amount of games that will be played
        chromosomes: List of chromosomes for a GA agent

    NOTE: the code could be simplified by passing an Agent object directly, however, Python erroneously points to the wrong
    'self' object whenever a method is executed if the agent is instantiated in a different thread, no idea why this occurs
    and there's nowhere in which this problem has been discussed.
    """
    global barrier
    global mutex
    global first

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((constants.HOST, constants.PORT))

        # Situational optimization (Repeat a given context to see what is the best move)

        if tid == 0:
            if player_type == "ga":
                player = agents.GAAgent(get_name())
            elif player_type == "random":
                player = agents.RandomAgent(get_name())
            else:
                player = agents.DeterministicAgent(get_name())
        else:
            player = agents.DeterministicAgent(get_name())

        # %% Adding player to the game
        request = gd.ClientPlayerAddData(player.name).serialize()

        sock.send(request)
        # Checking connection, exit if not done
        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)

        if type(data) is not gd.ServerPlayerConnectionOk:
            sys.exit("Error, could not correctly connect to the server")

        barrier.wait()
        mutex.acquire()
        if first:
            barrier.reset()
        first = False
        mutex.release()

        # %% Starting game

        sock.send(gd.ClientPlayerStartRequest(player.name).serialize())
        logging.debug(f"Sent -> {player.name} : {gd.ClientPlayerStartRequest}")

        logging.info(f"{player.name} joined")

        bypass = False
        players = None

        for _ in range(iterations):

            if player_type == "ga" and chromosomes:
                chromosome = chromosomes.pop()
                player.set_chromosome(chromosome)

            run = True
            played = False

            while run:

                barrier_turn_start.wait()
                barrier_turn_start.reset()

                try:

                    if not bypass:
                        data = sock.recv(constants.DATASIZE)
                        data = gd.GameData.deserialize(data)

                except:
                    run = False

                logging.debug(f"Received -> {player.name} : {type(data)}")

                if type(data) is gd.ServerStartGameData or (bypass and type(data) is gd.ServerGameOver):

                    if players is None:
                        players = data.players

                    # if tid == 0:
                    #     breakpoint()

                    handlers.handle_startgame_player(players, player, barrier, sock)
                    bypass = False


                elif type(data) is gd.ServerPlayerMoveOk:
                    logging.info("Good move")

                    # if tid == 0:
                    #     breakpoint()

                    if data.lastPlayer != player.name:
                        player.remove_hint_after_play(data.lastPlayer, data.cardHandIndex)

                    if slowmode:
                        time.sleep(0.5)
                    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

                elif type(data) is gd.ServerPlayerThunderStrike:
                    logging.info("Bad move")

                    # if tid == 0:
                    #     breakpoint()

                    if data.lastPlayer != player.name:
                        player.remove_hint_after_play(data.lastPlayer, data.cardHandIndex)

                    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

                elif type(data) is gd.ServerActionValid:
                    # Might be useful in the future, keeping track of how does each player plays

                    # if tid == 0:
                    #     breakpoint()

                    if slowmode:
                        time.sleep(0.5)

                    if data.lastPlayer != player.name:
                        player.remove_hint_after_play(data.lastPlayer, data.cardHandIndex)

                    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

                elif type(data) is gd.ServerActionInvalid:

                    logging.info(f"Player: {player.name} has done wrong.")

                    # breakpoint()

                    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

                elif type(data) is gd.ServerGameStateData:
                    # %% Code in which a decision is going to be taken

                    # if tid == 0:
                    #     breakpoint()

                    player.cull_visible_cards(data)

                    if data.currentPlayer == player.name and played:
                        logging.info(f"It's not {player.name}'s turn")
                        time.sleep(0.5)
                        sock.send(gd.ClientGetGameStateRequest(player.name).serialize())
                        played = False
                    elif data.currentPlayer == player.name:
                        handlers.handle_gamestate_player(data, player, sock)
                        played = True
                    else:
                        played = False


                elif type(data) is gd.ServerHintData:
                    # %% Managing received hints

                    # if tid == 0:
                    #     breakpoint()

                    handlers.handle_hint_player(data, player)

                    sock.send(gd.ClientGetGameStateRequest(player.name).serialize())
                    logging.debug(f"Sent -> {player.name} : {gd.ClientGetGameStateRequest}")

                elif type(data) is gd.ServerInvalidDataReceived:
                    # %% Managing bad code
                    logging.debug(f"Contents: {data.data}")

                elif type(data) is gd.ServerGameOver:
                    # %% Managing the end of the game

                    # breakpoint()

                    if(tid == 0):
                        if ret is not None:
                            ret.append(data.score)
                    run = False
                    first = True
                    mutex.acquire()
                    if first:
                        barrier.reset()
                        barrier_turn_start.reset()
                    first = False
                    mutex.release()

                barrier_turn_end.wait()
                barrier_turn_end.reset()

            logging.info("Game is over")
            # if tid == 0:
            #     breakpoint()

            bypass = True


def main(args: Namespace, ret: Optional[List[int]] = None):
    """

    Main function which will instantiate all the agents

    Args:
        args: Arguments passed in the command and parsed by argparse
        ret: Optional list which will return the scores
    """
    init_global_vars(args)

    chromosome = None
    if args.player_type == "ga":
        chromosome = [utility.make_chromosome(args)]

    threads = list()

    for i in range(args.num_players):
        if i == 0:
            t = Thread(target=player_thread, args=(i, ret, args.player_type, args.iterations, chromosome, args.slowmode))
        else:
            t = Thread(target=player_thread, args=(i, ret, "deterministic", args.iterations, None, args.slowmode))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if args.training and ret is not None:
        with open(f"{args.num_players}-deterministic.csv", 'a') as f:
            f.write(f"{ret[0]},")

def init_global_vars(args: Namespace):

    global barrier
    global barrier_turn_start
    global barrier_turn_end
    global mutex
    global names
    global first

    barrier = Barrier(args.num_players)
    barrier_turn_start = Barrier(args.num_players)
    barrier_turn_end = Barrier(args.num_players)
    mutex = Lock()
    first = True

    names = ["Richard", "Rasmus", "Tony", "Aubrey", "Don Juan", "Graham", "Dennis", "Jones"]

    logging.basicConfig(level=args.log, format="%(levelname)s %(threadName)s %(message)s")

# %% Main
if __name__ == "__main__":

    args = parse.parse_arguments()

    main(args)

