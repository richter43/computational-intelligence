#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 19:01:33 2021

@author: foxtrot
"""
from threading import Thread, Barrier, Lock
import sys
import socket
import logging
import numpy as np

import game
import constants
import GameData as gd
import utils.localparse as parse
import utils.handlers as handlers

# %% Global variables
names = set(["Richard", "Rasmus", "Tony", "Aubrey",
             "Don Juan", "Graham", "Dennis", "Jones"])

barrier = None
mutex = None
localGame = None
first = None

barrier_turn_start = None
barrier_turn_end = None


def get_name() -> str:
    """
    Takes, removes and returns a name from the list.
    This code is thread-safe.
    """

    global names
    global mutex

    mutex.acquire()
    name = np.random.choice(list(names), 1)[0]
    # Casting to regular string due to numpy being weird and having its own string type ????
    name = str(name)
    names.remove(name)
    mutex.release()

    return name


def player(tid: int) -> None:
    """
    Player instantiated in a separate thread
    """
    global barrier
    global localGame
    global mutex
    global first

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # Keep a local copy of all the possible cards
        card_set = set(localGame._Game__cardsToDraw)
        # Situational optimization (Repeat a given context to see what is the best move)
        name = get_name()
        num_cards = None
        own_cards = None
        # player_knowledge = None Implements what other players currently know about their cards, see if it's worth

        # %% Adding player to the game
        request = gd.ClientPlayerAddData(name).serialize()
        sock.connect((constants.HOST, constants.PORT))
        sock.send(request)
        # Checking connection, exit if not done
        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)

        if type(data) is not gd.ServerPlayerConnectionOk:
            sys.exit("Error, could not correctly connect to the server")

        barrier.wait()
        # %% Starting game
        sock.send(gd.ClientPlayerStartRequest(name).serialize())

        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)

        if tid == 0:
            barrier.reset()

        logging.debug(f"{name} start request")

        run = True
        count = 0

        while run:

            barrier_turn_start.wait()
            barrier_turn_start.reset()

            try:
                data = sock.recv(constants.DATASIZE)
                data = gd.GameData.deserialize(data)
            except:
                sock.close()
                return

            logging.debug(f"Received -> {name} : {data}")

            if type(data) is gd.ServerStartGameData:
                num_cards, own_cards = handlers.handle_startgame(
                    data, name, card_set, barrier, sock)

            elif type(data) is gd.ServerPlayerMoveOk or type(data) is gd.ServerPlayerThunderStrike:
                sock.send(gd.ClientGetGameStateRequest(name).serialize())

            elif type(data) is gd.ServerActionValid:
                # Might be useful in the future, keeping track of how does each player plays

                # if data.player == name: #Doesn't work, the name is that of the current player and not of the player who discarded the card
                #     # Removing the card from the set of possibilities and the global card tracker

                #     breakpoint()

                #     logging.debug(f"{name} removed {data.card}")

                #     card_set -= {data.card}
                #     for pos_card in own_cards:
                #         pos_card -= {data.card}

                sock.send(gd.ClientGetGameStateRequest(name).serialize())

            elif type(data) is gd.ServerGameStateData:
                handlers.handle_gamestate(
                    data, card_set, name, own_cards, sock)

            elif type(data) is gd.ServerHintData:
                handlers.handle_hint(data, own_cards, name)
                sock.send(gd.ClientGetGameStateRequest(name).serialize())
                logging.debug(
                    f"Sent -> {name} : {gd.ClientGetGameStateRequest}")

            elif type(data) is gd.ServerInvalidDataReceived:
                logging.debug(f"Contents: {data.data}")

            elif type(data) is gd.ServerGameOver:
                run = False

            barrier_turn_end.wait()
            barrier_turn_end.reset()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(relativeCreated)6d %(threadName)s %(message)s')

    args = parse.parse_arguments()

    am_players = args.num_players
    # Barriers used for simulating turns
    barrier = Barrier(am_players)
    barrier_turn_start = Barrier(am_players)
    barrier_turn_end = Barrier(am_players)
    mutex = Lock()
    first = True

    localGame = game.Game()

    threads = list()

    for i in range(am_players):
        t = Thread(target=player, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
