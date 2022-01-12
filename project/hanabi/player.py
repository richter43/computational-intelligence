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

import constants
import GameData as gd
import utils.localparse as parse
import utils.handlers as handlers
import utils.utility as utility
import agents

# %% Global variables
names = set(["Richard", "Rasmus", "Tony", "Aubrey", "Don Juan", "Graham", "Dennis", "Jones"])

barrier = None
mutex = None
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


def cut_and_return(data: bytes):

    """
    Splits the bytes information if there's more than one packet that was received
    """
    final_index = data.find(b"ub.") + 3

    if len(data) != final_index:
        return data[final_index:]

    return None


def player_thread(tid: int) -> None:
    """
    Player instantiated in a separate thread
    """
    global barrier
    global mutex
    global first

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # Situational optimization (Repeat a given context to see what is the best move)

        player = agents.RandomAgent(get_name())
        # player_knowledge = None Implements what other agents currently know about their cards, see if it's worth

        # %% Adding player to the game
        request = gd.ClientPlayerAddData(player.name).serialize()
        sock.connect((constants.HOST, constants.PORT))
        sock.send(request)
        # Checking connection, exit if not done
        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)

        if type(data) is not gd.ServerPlayerConnectionOk:
            sys.exit("Error, could not correctly connect to the server")

        barrier.wait()

        if tid == 0:
            barrier.reset()

        # %% Starting game

        sock.send(gd.ClientPlayerStartRequest(player.name).serialize())
        logging.debug(f"Sent -> {player.name} : {gd.ClientPlayerStartRequest}")

        logging.info(f"{player.name} joined")

        run = True
        queue = None

        while run:

            barrier_turn_start.wait()
            barrier_turn_start.reset()

            try:

                if queue is None:
                    data = sock.recv(constants.DATASIZE)
                    queue = cut_and_return(data)
                    data = gd.GameData.deserialize(data)

                else:
                    data = gd.GameData.deserialize(queue)
                    queue = cut_and_return(queue)
            except:
                sock.close()
                return

            logging.debug(f"Received -> {player.name} : {type(data)}")

            if type(data) is gd.ServerStartGameData:
                handlers.handle_startgame_player(data, player, barrier, sock)

            elif type(data) is gd.ServerPlayerMoveOk:
                logging.info("Good move")
                sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

            elif type(data) is gd.ServerPlayerThunderStrike:
                logging.info("Bad move")

                sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

            elif type(data) is gd.ServerActionValid:
                # Might be useful in the future, keeping track of how does each player plays

                # if data.player == name: #Doesn't work, the name is that of the current player and not of the player who discarded the card
                #     # Removing the card from the set of possibilities and the global card tracker

                #     breakpoint()

                #     logging.debug(f"{name} removed {data.card}")

                #     card_set -= {data.card}
                #     for pos_card in own_cards:
                #         pos_card -= {data.card}

                sock.send(gd.ClientGetGameStateRequest(player.name).serialize())

            elif type(data) is gd.ServerGameStateData:
                # %% Code in which a decision is going to be taken

                if tid == 0:
                    breakpoint()
                    a = utility.final_randomvar_score(data, player)

                handlers.handle_gamestate_player(data, player, sock)

            elif type(data) is gd.ServerHintData:
                # %% Managing received hints
                handlers.handle_hint_player(data, player)

                sock.send(gd.ClientGetGameStateRequest(player.name).serialize())
                logging.debug(f"Sent -> {player.name} : {gd.ClientGetGameStateRequest}")

            elif type(data) is gd.ServerInvalidDataReceived:
                # %% Managing bad code
                logging.debug(f"Contents: {data.data}")

            elif type(data) is gd.ServerGameOver:
                # %% Managing the end of the game
                logging.info("Bad move")
                run = False

            barrier_turn_end.wait()
            barrier_turn_end.reset()

        logging.info("Game is over")


# %% Main
if __name__ == "__main__":

    args = parse.parse_arguments()

    logging.basicConfig(level=args.log, format="%(levelname)s %(threadName)s %(message)s")

    am_players = args.num_players
    # Barriers used for simulating turns
    barrier = Barrier(am_players)
    barrier_turn_start = Barrier(am_players)
    barrier_turn_end = Barrier(am_players)
    mutex = Lock()
    first = True

    threads = list()

    for i in range(am_players):
        t = Thread(target=player_thread, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
