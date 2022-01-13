#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 23:04:07 2021

@author: foxtrot
"""
from threading import Thread
from typing import List, Dict, Set, Tuple
import numpy as np
from operator import itemgetter

from agents import Agent
import game
import GameData as gd

Suit = str


def playable(card: game.Card, table_state: Dict[Suit, List[int]]) -> bool:

    pile = table_state[card.color]

    return card.value == len(pile) + 1


def rarity(card: game.Card, playable_cards: Set[game.Card]) -> float:

    values_present = sum([card.value == set_card.value and card.color == set_card.color for set_card in playable_cards])

    return 1 / values_present


def utility(card: game.Card, data: gd.ServerGameStateData, player: Agent):

    if playable(card, data.tableCards):
        # Playability is more important than rarity
        return 1.1

    other_player_cards = set([card for data_player in data.players for card in data_player.hand])
    return rarity(card, player.total_possible_cards | other_player_cards)


def hint_bestplayerpos(data: gd.ServerGameStateData, player: Agent) -> Tuple[str, int]:

    dict_player_cards = {}
    max_num = -1

    for data_player in data.players:
        dict_player_cards[data_player.name] = np.array([utility(card, data, player) for card in data_player.hand])
        max_tmp = max(dict_player_cards[data_player.name])
        max_num = max(max_tmp, max_num)

    list_player_pos_score = [
        ((other_player, np.argmax(util_list)), np.sum(max_num == util_list))
        for other_player, util_list in dict_player_cards.items()
    ]

    return max(list_player_pos_score, key=itemgetter(1))[0]


def randomvar_score(
    cloud_cards: Set[game.Card], data: gd.ClientGetGameStateRequest, player: Agent, result_list: List[float], tid: int
):

    tmp_score = [utility(card, data, player) for card in cloud_cards]
    result_list[tid] = np.average(tmp_score)


def final_randomvar_score(data: gd.ServerGameStateData, player: Agent) -> float:

    # TODO WRONG!!!!! Use threads for splitting the work of each cloud_cards

    thread_list = list()
    result_list = np.zeros(player.num_cards)

    tid = 0

    for cloud_cards in player.hand_possible_cards:
        t = Thread(
            target=randomvar_score,
            args=(
                cloud_cards,
                data,
                player,
                result_list,
                tid,
            ),
        )
        thread_list.append(t)
        t.start()
        tid += 1

    for t in thread_list:
        t.join()

    return result_list

def playable_percentage(cloud_cards: Set[game.Card], table_state: Dict[Suit, List[int]]) -> float:

    #TODO dividing by zeor, check

    can_play = 0

    for card in cloud_cards:
        if playable(card, table_state):
            can_play+=1

    return can_play/len(cloud_cards)

def player_playable_card(player_list: List[game.Player], table_state: Dict[Suit, List[int]]) -> Tuple[str, str, object]:

    pos_hint = ["value", "color"]
    pos_cards = []

    for server_player in player_list:
        for card in server_player.hand:
            if playable(card, table_state):
                pos_cards.append((server_player.name, card))

    if len(pos_cards) == 0:
        return None
    card_idx = np.random.choice(len(pos_cards), 1)[0]
    hint_type = np.random.choice(pos_hint, 1)[0]

    if hint_type == "value":
        hint = pos_cards[card_idx][1].value
    else:
        hint = pos_cards[card_idx][1].color

    return (pos_cards[card_idx][0], hint_type, hint)

def least_info_card(list_cloud_cards: List[Set[game.Card]]) -> int:

    size_pos = np.array([len(cloud_card) for cloud_card in list_cloud_cards])

    posssible_idxs = np.array(range(len(list_cloud_cards)))[size_pos == np.max(size_pos)]

    return np.random.choice(posssible_idxs,1)[0]

def random_hint(players: List[game.Player]):
    types = ["value", "color"]

    player = np.random.choice(players, 1)[0]
    card = np.random.choice(player.hand, 1)[0]
    sel_type = np.random.choice(types, 1)[0]

    if sel_type == "value":
        value = card.value
    else:
        value = card.color

    return (player.name, sel_type, value)