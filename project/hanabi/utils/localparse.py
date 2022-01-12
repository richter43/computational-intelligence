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

    args = args.parse_args()

    args.log = getattr(logging, args.log.upper())

    return args
