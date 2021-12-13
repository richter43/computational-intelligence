#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 19:01:33 2021

@author: foxtrot
"""

import pdb
import sys
import GameData as gd
import constants
import socket
import numpy as np
import time
from threading import Thread, Barrier, Lock

names = set(["Richard", "Rasmus", "Tony", "Aubrey",
             "Don Juan", "Graham", "Dennis", "Jones"])

barrier = None
mutex = None


def random_play(name):
    plays = list(range(5))
    play = np.random.choice(plays, 1)[0]
    request = gd.ClientPlayerPlayCardRequest(name, play).serialize()
    return request


def player(id):

    global names
    global barrier
    global mutex

    print(id)

    card_set = None  # Keep a local copy of all the possible cards
    # Situational optimization (Repeat a given context to see what is the best move)

    mutex.acquire()
    name = np.random.choice(list(names), 1)[0]
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

        barrier.reset()

        # pdb.set_trace()
        mutex.acquire()
        sock.send(gd.ClientPlayerStartRequest(name).serialize())
        # time.sleep(0.1)
        mutex.release()

        print(f"{name} start request")
        barrier.wait()
        sock.send(gd.ClientPlayerReadyData(name).serialize())
        counter = 0
        run = True
        start = False

        while run:

            data = sock.recv(constants.DATASIZE)
            data = gd.GameData.deserialize(data)

            print(f"{counter} -> {name}: {data}")
            counter += 1

            if type(data) is gd.ServerStartGameData:

                sock.send(gd.ClientGetGameStateRequest(name).serialize())

            # elif type(data) is gd.ServerStartGameData or type(data) is gd.ServerPlayerMoveOk or type(data) is gd.ServerPlayerThunderStrike:
            # elif type(data) is gd.ServerPlayerMoveOk or type(data) is gd.ServerPlayerThunderStrike:
            #     sock.send(gd.ClientGetGameStateRequest(name).serialize())

            # elif type(data) is gd.ServerActionValid:
            #     # Might be useful in the future, keeping track of how does each player plays

            #     sock.send(gd.ClientGetGameStateRequest(name).serialize())

            elif type(data) is gd.ServerGameStateData:

                print(f"Current player: {data.currentPlayer}")
                if data.currentPlayer == name:
                    request = random_play(name)
                    sock.send(request)
            elif type(data) is gd.ServerGameOver:
                run = False

        return 0


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Error, number of players must be given as an argument")

    am_players = int(sys.argv[1])
    barrier = Barrier(am_players)
    mutex = Lock()

    threads = list()

    for i in range(am_players):
        t = Thread(target=player, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
