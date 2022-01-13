#


import numpy as np

from .agent_interface import Agent, Action
from .random_agent import RandomAgent
from .deterministic_agent import DeterministicAgent

a = [RandomAgent, DeterministicAgent]

def get_random_player():

    return np.random.choice(a, 1)[0]
