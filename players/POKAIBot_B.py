from pickle import load
from random import random
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from effective_hand_strength import HandStrengthEval
NUM_TO_ACTION = {"1": "call", "0": "fold", "2": "raise"}
NB_SIMULATION = 200

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

class POKAIPlayerB(BasePokerPlayer):

    def __init__(self):
        BasePokerPlayer.__init__(self)
        self.strategy = load(open("strats/job_1000.strat"))
        # self.communities = load(open("3hand_cleaned.group"))
        # self.holes = load(open("2hand_groups_py2.cards"))
        self.hand_strength_eval = HandStrengthEval()

    def get_higher_rank(self, card1, card2):
        if card1.rank > card2.rank:
            return card1
        return card2

    def simplify_hand(self, hand, community_cards):
        """ Takes a hand (array of size two) and compresses the hand into simpler representation
            Also puts higher card in front
            i.e. Th 9h becomes T9s as both cards share the same suit
                Th 9s becomes T9o as both cards do not share the same suit (off-suit)
                Th Ts becomes TT (pair of tens)
        """
        generated_hand = gen_cards(hand)
        card1 = generated_hand[0]
        card2 = generated_hand[1]

        # pair
        if card1.rank == card2.rank:
            # print "Pair %s" % str(card1)[1] + str(card2)[1]
            return str(card1)[1] + str(card2)[1] # return the rank 2-9, J-A instead of all ints

        hand = str(self.get_higher_rank(card1, card2))[1]
        # print "Higher rank card %s" % hand
        hand += str(card2)[1] if hand == str(card1)[1] else str(card1)[1]
        hand += str("s") if str(card1)[0] == str(card2)[0] else str("o")
        # print "final hand %s" % hand

        if len(community_cards) >= 3:
          strength = HandEvaluator.gen_hand_rank_info(generated_hand, gen_cards(community_cards))
          hand += "_%s" %strength.get("hand")["strength"]

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
        
        # if round_state["street"] == "river" or round_state["street"] == "turn":
        #     #print "reached river"
        #     hs = self.hand_strength_eval.hand_strength(hole_card, round_state["community_card"])
        #     pot = round_state["pot"]["main"]["amount"]
        #     expected_if_call = hs*pot - (1-hs)*pot
        #     expected_if_raise = hs*(pot+40) - (1-hs)*(pot+40)
        #     if expected_if_call < expected_if_raise and can_raise:
        #         return "raise"
        #     else:
        #         return "call"

        # query_string = self.simplify_hand(hole_card, round_state["community_card"])
        # query_string += action_str
        # if query_string in self.strategy:
        #     action = NUM_TO_ACTION[random_sample(self.strategy[query_string])]
            
        #     if not can_raise and action == "raise":
        #         return "call"
            
        #     return action
        # # print "couldn't find move"
        # community_card = round_state['community_card']
        # win_rate = estimate_hole_card_win_rate(
        #     nb_simulation = NB_SIMULATION,
        #     nb_player = self.num_players,
        #     hole_card = gen_cards(hole_card),
        #     community_card = gen_cards(community_card)
        # )

        # # print("HonestP hole card: "+ str(hole_card))
        # # print("Winrate: "+ str(win_rate))
        
        # if win_rate >= 0.35:
        #     if win_rate > 0.7:
        #         action = valid_actions[2]['action'] if can_raise else valid_actions[1]['action']
        #     else:
        #         action = valid_actions[1]['action']
        # else:
        #     action = "fold"

        if round_state["street"] == "river" or round_state["street"] == "turn":
            #print "reached river"
            community_card = round_state['community_card']
            #print self.paid_sum()
            win_rate = estimate_hole_card_win_rate(
                nb_simulation = 300,
                nb_player = 2,
                hole_card = gen_cards(hole_card),
                community_card = gen_cards(community_card))
            if win_rate >= 0.5:
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
        # return action

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # print(winners)
        pass


def setup_ai():
  return POKAIPlayerB()
