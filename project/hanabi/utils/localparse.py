#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 22:54:49 2021

@author: foxtrot
"""

import argparse


def parse_arguments() -> argparse.Namespace:

    args = argparse.ArgumentParser()

    args.add_argument("--num_players", type=int, default=1,
                      help="Number of players")

    args = args.parse_args()

    return args
