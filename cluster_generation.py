#!/usr/bin/env python
# coding: utf-8
from utils.utility import *
from effective_hand_strength import HandStrengthEval

hand_strength_evaluator = HandStrengthEval()

cards = get_all_possible_cards()
flop_cards = get_all_combinations(cards, 3)
remainder_cards = get_all_combinations(cards, 2)



import pickle
hand_groups = pickle.load(open("2hand_groups.cards", "rb"))
cards_in_handgroup ={}
for c in hand_groups:
    if hand_groups[c] not in cards_in_handgroup:
        cards_in_handgroup[hand_groups[c]] = []
    cards_in_handgroup[hand_groups[c]].append(c)



from random import choice
import numpy as np

def contains_card_from_set(card_group, remainder):
    """
    Utility method
    """
    for c in remainder:
        if c in card_group:
            return True
    return False

def get_card_group(res):
    if str(res[0:2]) in hand_groups:
        return hand_groups[str(res[0:2])]
    else:
        return hand_groups[str(res[0:2][::-1])]
    

def mc_get_card_group_hist(hand, remainder, num_samples=1000, hist_res=100):
    """
    Returns the histogram probability of winning using different
    cards.
    """
    lst = {}
    remainder = list(filter(lambda x: x not in hand, remainder))
    for i in range(num_samples):
        res = choice(remainder)
        group = get_card_group(res)
        hs = hand_strength_evaluator.hand_strength(hand, res)
        if group not in lst:
            lst[group] = {str(hand): []}
        lst[group][str(hand)].append(hs)
    return lst


from multiprocessing import Pool
NUM_PROCESSES = 4
START_IDX = 0
END_IDX = 4

def workload(card_hand):
    return mc_get_card_group_hist(card_hand, remainder_cards)

with Pool(NUM_PROCESSES) as pool:
    result = pool.map(workload, flop_cards[START_IDX: END_IDX])

pickle.dump(result, open("3hands.card", "wb+"))

