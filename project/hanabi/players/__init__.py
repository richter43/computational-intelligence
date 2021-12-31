#


import numpy as np

from .player_interface import Player
from .random_player import RandomPlayer

a = [RandomPlayer]


def get_random_player():

    return np.random.choice(a, 1)[0]
