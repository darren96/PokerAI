from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import pprint

NB_SIMULATION = 1000

class HonestPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    community_card = round_state['community_card']
    win_rate = estimate_hole_card_win_rate(
      nb_simulation = NB_SIMULATION,
      nb_player = self.num_players,
      hole_card = gen_cards(hole_card),
      community_card = gen_cards(community_card)
    )

    can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
    can_raise = len([item for item in valid_actions if item['action'] == 'raise']) > 0

    # print("HonestP hole card: "+ str(hole_card))
    # print("Winrate: "+ str(win_rate))
    
    if win_rate >= 0.35:
      if win_rate > 0.7:
        action = valid_actions[2]['action'] if can_raise else valid_actions[1]['action']
      else:
        action = valid_actions[1]['action']
    else:
      action = "fold"
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    self.num_players = game_info['player_num']

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    # print("My ID (round result - random) : "+self.uuid)
    # pprint.pprint(round_state)
    pass

def setup_ai():
  return HonestPlayer()
