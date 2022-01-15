#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 22:54:49 2021

@author: foxtrot
"""

import argparse
import logging


def parse_arguments() -> argparse.Namespace:

    args = argparse.ArgumentParser()

    args.add_argument("--num_players", type=int, default=1,
                      help="Number of agents")
    args.add_argument("--log", type=str, default="info",
                      choices=["info", "debug"])
    args.add_argument("--iterations", type=int, default=1)
    args.add_argument("--training", action='store_true')
    args.add_argument("--player_type", type=str, choices=["random", "ga", "deterministic"])
    args.add_argument("--ga_max_playability", type=float, default=0.6)
    args.add_argument("--random_discard", type=float, default=0.5)
    args.add_argument("--random_hint", type=float, default=0.5)

    args = args.parse_args()

    args.log = getattr(logging, args.log.upper())

    return args
