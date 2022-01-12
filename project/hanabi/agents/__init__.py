#


import numpy as np

from .agent_interface import Agent
from .random_agent import RandomAgent

a = [RandomAgent]


def get_random_player():

    return np.random.choice(a, 1)[0]
