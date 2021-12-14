#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 19:01:33 2021

@author: foxtrot
"""
from copy import deepcopy
import logging
import pdb
import sys
import GameData as gd
import constants
import socket
import numpy as np
import time
import game
from threading import Thread, Barrier, Lock, currentThread

names = set(["Richard", "Rasmus", "Tony", "Aubrey",
             "Don Juan", "Graham", "Dennis", "Jones"])

barrier = None
mutex = None
localGame = None


def random_play(name):
    plays = list(range(4))
    play = int(np.random.choice(plays, 1)[0])
    logging.debug(f"{name} played {play}")
    request = gd.ClientPlayerPlayCardRequest(name, play).serialize()
    return request


def player():

    global names
    global barrier
    global mutex
    global localGame

    mutex.acquire()

    mutex.release()
    # Keep a local copy of all the possible cards

    card_set = set(localGame._Game__cardsToDraw)
    seen_cards = list()
    player_dict = dict()
    # Situational optimization (Repeat a given context to see what is the best move)

    mutex.acquire()
    name = np.random.choice(list(names), 1)[0]
    # Casting to regular string due to numpy being weird and having its own string type ????
    name = str(name)
    names.remove(name)
    mutex.release()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        request = gd.ClientPlayerAddData(name).serialize()
        sock.connect((constants.HOST, constants.PORT))
        sock.send(request)

        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)

        if type(data) is not gd.ServerPlayerConnectionOk:
            sys.exit("Error, could not correctly connect to the server")

        barrier.wait()

        sock.send(gd.ClientPlayerStartRequest(name).serialize())
        data = sock.recv(constants.DATASIZE)
        data = gd.GameData.deserialize(data)
        barrier.reset()

        logging.debug(f"{name} start request")

        run = True

        while run:

            data = sock.recv(constants.DATASIZE)
            data = gd.GameData.deserialize(data)

            logging.debug(f"Received -> {name} : {data}")

            if type(data) is gd.ServerStartGameData:

                sock.send(gd.ClientPlayerReadyData(name).serialize())
                logging.debug(f"Sent -> {name} : {gd.ClientPlayerReadyData}")
                barrier.wait()
                sock.send(gd.ClientGetGameStateRequest(name).serialize())
                logging.debug(
                    f"Sent -> {name} : {gd.ClientGetGameStateRequest}")

            elif type(data) is gd.ServerPlayerMoveOk or type(data) is gd.ServerPlayerThunderStrike:
                sock.send(gd.ClientGetGameStateRequest(name).serialize())

            # elif type(data) is gd.ServerActionValid:
            #     # Might be useful in the future, keeping track of how does each player plays

            #     sock.send(gd.ClientGetGameStateRequest(name).serialize())

            elif type(data) is gd.ServerGameStateData:
                # pdb.set_trace()
                # for p in data.players:
                #     card_set -= set(p.hand)
                #     print(card_set)

                logging.debug(f"Current player: {data.currentPlayer}")
                if data.currentPlayer == name:
                    request = random_play(name)
                    sock.send(request)
            elif type(data) is gd.ServerGameOver:
                run = False

        return 0


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(relativeCreated)6d %(threadName)s %(message)s')

    if len(sys.argv) != 2:
        sys.exit("Error, number of players must be given as an argument")

    am_players = int(sys.argv[1])
    barrier = Barrier(am_players)
    mutex = Lock()
    localGame = game.Game()

    threads = list()

    for _ in range(am_players):
        t = Thread(target=player)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
