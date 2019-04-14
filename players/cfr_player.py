from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
from cfr_v2 import CFR
import pprint

class CfrPlayer(BasePokerPlayer):

  def __init__(self):
    self.util = 0.0
    # self.game_states_ = dict()  # maps history to node
    self.cfr = CFR()

  def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_pp = pprint.PrettyPrinter(indent=2)

    hole_card = gen_cards(hole_card)
    community_card = gen_cards(round_state['community_card'])

    round_h = round_state['action_histories']
    
    preflop_str = ''
    flop_str = ''
    turn_str = ''
    river_str = ''

    for key,val in round_h.iteritems():
      for action in val:
        if action['uuid'] == self.uuid:
          if key == 'preflop':
           preflop_str += action['action']
          elif key == 'flop':
           flop_str += action['action']
          elif key == 'turn':
           turn_str += action['action']
          elif key == 'river':
           river_str += action['action']
      
    state = str(hole_card) + str(community_card) + preflop_str + flop_str + turn_str + river_str
            
    print "state: " + str(state)         
    print "game states: " + str(self.game_states_.keys())
        
    if state in self.game_states_:
        node = self.game_states_[state] # Get our node if it already exists
    else:
        node = Node(valid_actions)
        self.game_states_[state] = node  

    node_util = 0

    
    return action

  def receive_game_start_message(self, game_info):
    self.num_players = game_info['player_num']

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass
    # pprint.pprint(hand_info)


def setup_ai():
  return CfrPlayer()

class Node:
    def __init__(self, actions):
        self.actions_ = actions
        self.regret_sum_ = dict()
        self.strategy_ = dict()
        self.strategy_sum_ = dict()

        for action in actions:
            self.regret_sum_[action] = 0.0
            self.strategy_[action] = 0.0
            self.strategy_sum_[action] = 0.0

    def get_strategy(self, realization_weight):
        normalizing_sum = 0

        for action in self.actions_:
            self.strategy_[action] = self.regret_sum_[action] if self.regret_sum_[action] > 0 else 0
            normalizing_sum += self.strategy_[action]

        for action in self.actions_:
            if normalizing_sum > 0:
                self.strategy_[action] /= normalizing_sum
            else:
                self.strategy_[action] = 1.0 / len(self.actions_)

            self.strategy_sum_[action] += realization_weight * self.strategy_[action]

        return self.strategy_

    def get_average_strategy(self):
        average_strategy = dict
        normalizing_sum = 0

        for action in self.actions_:
            normalizing_sum += self.strategy_sum_[action]

        for action in self.actions_:
            if normalizing_sum > 0:
                average_strategy[action] = self.strategy_sum_[action] / normalizing_sum
            else:
                average_strategy[action] = 1.0 / len(self.actions_)

        return average_strategy
