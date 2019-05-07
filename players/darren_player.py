from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator
import effective_hand_strength
import pprint

NB_SIMULATION = 1000
opponent_calls = 1
opponent_raises = 1

class DarrenPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    # pprint.pprint(round_state)
    community_card = round_state['community_card']
    win_rate = estimate_hole_card_win_rate(
      nb_simulation = NB_SIMULATION,
      nb_player = self.num_players,
      hole_card = gen_cards(hole_card),
      community_card = gen_cards(community_card)
    )
    gened_hole_card = gen_cards(hole_card)
    gened_community_card = gen_cards(community_card)
    street = round_state["street"]
    print("Street: %s" %street)
    print("Hole: %s" %hole_card.__str__())
    if street != "flop" and street != "preflop":
      community_card_in_hand = get_community_card_in_hand(gened_hole_card, gened_community_card)

    can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
    can_raise = len([item for item in valid_actions if item['action'] == 'raise']) > 0

    if win_rate >= 0.35:
      if win_rate > 0.7:
        action = valid_actions[2]['action'] if can_raise else valid_actions[1]['action']
      else:
        action = valid_actions[1]['action']
    else:
      action = "call" if can_call else "fold"

    if opponent_raises / opponent_calls > 1:
      action = "raise" if can_raise else "call"
      # print("opponent is aggresive")
    else:
      # print("opponent is passive")
      action = "call"
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    self.num_players = game_info['player_num']
    

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    global opponent_calls
    global opponent_raises
    actions = round_state["action_histories"][street]
    opponent_calls += len([action for action in actions if action['uuid'] != self.uuid and action['action'] == "CALL"])
    opponent_raises += len([action for action in actions if action['uuid'] != self.uuid and action['action'] == "RAISE"])
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

def setup_ai():
  return DarrenPlayer()

def get_community_card_in_hand(hole_card, community_card):
  rank_info = HandEvaluator.gen_hand_rank_info(hole_card, community_card)
  hand = rank_info.get("hand")
  strength = hand["strength"]
  print(strength)
  community_card_in_hand = sorted(community_card, reverse=True)
  for card in community_card_in_hand:
    if len(community_card_in_hand) == 3:
      break
    if not (card.rank == hand["low"] or card.rank == hand["high"]):
      if not(strength == "FLASH" or strength == "STRAIGHTFLASH" and \
          (hole_card[0].suit != card.suit or hole_card[1].suit != card.suit)):
        community_card_in_hand.remove(card)
  i = 0
  while i < len(community_card_in_hand):
    community_card_in_hand[i] = community_card_in_hand[i].__str__()
    i = i + 1

  return community_card_in_hand
