from pickle import load
from random import random

from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards

from pypokerengine.players import BasePokerPlayer
from effective_hand_strength import HandStrengthEval
NUM_TO_ACTION = {"2": "raise", "0": "fold", "1": "call"}

def random_sample(dct):
    prob = []
    accum = 0
    for i in dct:
        accum += dct[i]
        prob += [(accum, i)]
    
    v = random()

    for cumprb, action in prob:
        if cumprb > v:
            return action
    return action

class POKAIPlayer(BasePokerPlayer):

    def __init__(self):
        BasePokerPlayer.__init__(self)
        self.strategy = load(open("no_fold_cfr.strat"))
        self.communities = load(open("3hand_cleaned.group"))
        self.holes = load(open("2hand_groups_py2.cards"))
        self.hand_strength_eval = HandStrengthEval()

    def simplify_hand(self, hand, community_cards):
        """ Takes a hand (array of size two) and compresses the hand into simpler representation
            Also puts higher card in front
            i.e. Th 9h becomes T9s as both cards share the same suit
                Th 9s becomes T9o as both cards do not share the same suit (off-suit)
                Th Ts becomes TT (pair of tens)
        """
        card1 = hand[0]
        card2 = hand[1]

        key1 = "('%s', '%s')" % (card1, card2)
        key2 = "('%s', '%s')" % (card2, card1)

        if key1 in self.holes:
            hole_group = self.holes[key1]
            hole = "_%dG" % self.holes[key1]
        elif key2 in self.holes:
            hole_group = self.holes[key2]
            hole = "_%dG" % self.holes[key2]

        hand = hole

        if len(community_cards) != 0:
            community_cards = sorted(community_cards)
            key = (community_cards[0], community_cards[1], community_cards[2])

            if self.communities[hole_group].has_key(key):
                hand = "%s_%dG" % (hole, self.communities[hole_group].get(key))

        return hand
    
    def declare_action(self, valid_actions, hole_card, round_state): 
        #print "round_state"
        lst = []
        if "preflop" in round_state["action_histories"]:
            lst += round_state["action_histories"]["preflop"]
        if "flop" in round_state["action_histories"]:
            lst += round_state["action_histories"]["flop"]
        if "turn" in round_state["action_histories"]:
            lst += round_state["action_histories"]["turn"]
        if "river" in round_state["action_histories"]:
            lst += round_state["action_histories"]["river"]
        
        action_str = ""
        for action in lst:
            if action["action"] == "CALL":
                action_str += "1"
            elif action["action"] == "RAISE":
                action_str += "2"
        
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        can_raise = len([item for item in valid_actions if item['action'] == 'raise']) > 0
        
        if round_state["street"] == "river" or round_state["street"] == "turn":
            #print "reached river"
            community_card = round_state['community_card']
            #print self.paid_sum()
            win_rate = estimate_hole_card_win_rate(
                nb_simulation = 300,
                nb_player = 2,
                hole_card = gen_cards(hole_card),
                community_card = gen_cards(community_card))
            if win_rate >= 0.35:
                if win_rate > 0.75:
                    action = valid_actions[2]['action'] if can_raise else valid_actions[1]['action']
                else:
                    action = valid_actions[1]['action']
            else:
                action = valid_actions[1]['action'] if can_call else valid_actions[0]['action']
            return action

        query_string = self.simplify_hand(hole_card, round_state["community_card"])
        query_string += action_str
        if query_string in self.strategy:
            action = NUM_TO_ACTION[random_sample(self.strategy[query_string])]
            
            if not can_raise and action == "raise":
                return "call"
            
            return action
        print "couldn't find move"
        return "raise"

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        print winners


def setup_ai():
  return NNPlayer()
