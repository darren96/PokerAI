from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
from multiprocessing import Pool
import pickle

ITERATIONS = 8000
ACTION_TO_HISTORY_MAPPING = {"fold": "0", "call": "1", "raise": "2", "small_blind": "3", "big_blind": "4", "ante": "5"}
HISTORY_TO_ACTION_MAPPING = {"0": "fold", "1": "call", "2": "raise", "3": "small_blind", "4": "big_blind", "5": "ante"}


class CFR:
    def __init__(self):
        self.game_states_ = dict()  # maps history to node
        self.emulator = Emulator()

    @staticmethod
    def get_higher_rank(card1, card2):
        if card1.rank > card2.rank:
            return card1
        return card2

    @staticmethod
    def get_higher_suit(card1, card2):
        if card1.suit > card2.suit:
            return card1
        elif card1.suit == card2.suit:
            return 0
        return card2

    @staticmethod
    def simplify_hand(hand, community_cards):
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

        hand = str(CFR.get_higher_rank(card1, card2))[1]
        # print "Higher rank card %s" % hand
        hand += str(card2)[1] if hand == str(card1)[1] else str(card1)[1]
        hand += str("s") if str(card1)[0] == str(card2)[0] else str("o")
        # print "final hand %s" % hand

        if len(community_cards) >= 3:
          strength = HandEvaluator.gen_hand_rank_info(generated_hand, gen_cards(community_cards))
          hand += "_%s" %strength.get("hand")["strength"]

        return hand


    def train(self, iterations, ante=1.0, bet1=2.0, bet2=8.0, print_interval=1000, save_interval=1000):
        """ Do ficticious self-play to find optimal strategy"""
        util = 0.0

        self.ante = ante
        self.bet1 = bet1
        self.bet2 = bet2

        # print "Ante: %f   Bet-1: %f   Bet-2: %f" % (ante, bet1, bet2)

        for i in range(iterations):
            if i % print_interval == 0 and i != 0:
                print("P1 expected value after %i iterations: %f" % (i, util / i))
                # for j in range(-1, 17):
                #     try:
                #         print j, strats["_" + str(j) + "G"]
                #     except:
                #         pass

            self.emulator.set_game_rule(2, 5, 10, 5)
            init_state = self.emulator.generate_initial_game_state(
                {"0": {"stack": 10000, "name": "0"}, "1": {"stack": 10000, "name": "1"}})
            round_start, events = self.emulator.start_new_round(init_state)
            player_one_cards = list(map(str, round_start["table"].seats.players[0].hole_card))
            player_two_cards = list(map(str, round_start["table"].seats.players[1].hole_card))
            cards = [player_one_cards, player_two_cards]
            history = list()
            util += self.cfr(cards, history, round_start, events, 1, 1)
            # strats = self.get_strategy()

            # """
            # if i%save_interval == 0:
            #     print "saving..."
            #     pickle.dump(self.get_strategy(), open("full_game_"+str(i)+"_avg_diff.strat", "wb"))
            # """
        return util / iterations

    def get_strategy(self):
        result = dict()
        for state, node in self.game_states_.items():
            #print(state, node.strategy_)
            result[state] = node.get_average_strategy()
        return result

    # @cards - the cards the players have, with index 0 being the card that player one has
    # and index 1 being the card that player two has
    # @history - a list of moves used to reach this game state
    # @probability1 - the probability of reaching this game state for player 1
    # @probability2 - the probability of reaching this game state for player 2
    # @game_state - PyPokerEngine's game state.
    def cfr(self, cards, history, game_state, events, probability1, probability2):
        player = 1-int(game_state["next_player"])
        opponent = 1 - player
        player_hand = cards[player]
        # print "=========== PLAYER " + str(player) + " TURN ==============="
        # print "history: " + str(history)
        # print "player_hand: %s %s" % (str(player_hand[0]), str(player_hand[1]))
        # print "opp_hand: %s %s" % (str(opponent_hand[0]), str(opponent_hand[1]))

        probability_weight = probability1 if player == 0 else probability2

        # print "probability_weight: " + str(probability_weight)event["round_state"]
        # print "num_moves: " + str(num_moves)

        # BEGIN TERMINAL STATES
        for event in events:
            if event["type"] == "event_round_finish":
                dct = {}
                dct[game_state["table"].seats.players[0].uuid] = game_state["table"].seats.players[0].stack
                dct[game_state["table"].seats.players[1].uuid] = game_state["table"].seats.players[1].stack
                #print (game_state, event)
                #print "player", player
                return dct[str(player)] - dct[str(opponent)]

        community_card = []
        for i in range(len(game_state["table"].get_community_card())):
            community_card.append(game_state["table"].get_community_card()[i].__str__())

        # state = str(player_hand)
        p_hand = self.simplify_hand(player_hand, community_card)
        state = str(p_hand)

        for action in history:
            state += action

        # print "state: %s" % str(state)
        # CREATE NEW ACTIONS

        if state in self.game_states_:
            node = self.game_states_[state]  # Get our node if it already exists
            possible_actions = node.actions_
        else:
            # Create new Node with possible actions we can perform
            possible_actions = [ACTION_TO_HISTORY_MAPPING[i["action"]] for i in
                                self.emulator.generate_possible_actions(game_state)]
            node = Node(possible_actions)
            self.game_states_[state] = node

        strategy = node.get_strategy(probability_weight)

        # print "possible_actions for this round: " + str(possible_actions)
        # print "strategy: " + str(strategy)

        util = dict()
        node_util = 0
        # for each of our possible actions, compute the utility of it
        # thus, finding the overall utility of this current state
        for action in possible_actions:
            next_history = list(history)  # copy
            next_history.append(action)
            new_game_state, new_event = self.emulator.apply_action(game_state, HISTORY_TO_ACTION_MAPPING[action])

            if player == 0:
                util[action] = -self.cfr(cards, next_history, new_game_state, new_event,
                                         probability1 * strategy[action], probability2)
            else:
                util[action] = -self.cfr(cards, next_history, new_game_state, new_event, probability1,
                                         probability2 * strategy[action])
            #print action, util[action]
            node_util += strategy[action] * util[action]

        # compute regret and update Game State for the node based on utility of all actions
        for action in possible_actions:
            regret = util[action] - node_util
            if player == 0:
                node.regret_sum_[action] += regret * probability2
            else:
                node.regret_sum_[action] += regret * probability1

        #print "node_util: "+ str(action) + " " + str(node_util)

        return node_util


cfr = CFR()


# player_one_cards, player_two_cards = Game.deal_cards()
# p1_hand = cfr.simplify_hand(player_one_cards)
# p2_hand = cfr.simplify_hand(player_two_cards)
# print cfr.get_winner(player_one_cards, player_two_cards)

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
        average_strategy = dict()
        normalizing_sum = 0

        for action in self.actions_:
            normalizing_sum += self.strategy_sum_[action]

        for action in self.actions_:
            if normalizing_sum > 0:
                average_strategy[action] = self.strategy_sum_[action] / normalizing_sum
            else:
                average_strategy[action] = 1.0 / len(self.actions_)

        return average_strategy


def jobWrapper(i):
    ante = 5.0
    bet1 = 10.0
    bet2 = 20.0
    util = cfr.train(ITERATIONS, ante, bet1, bet2)
    print("Player One Expected Value Per Hand: %f" % util)
    result = cfr.get_strategy()
    # print "Final strategy: " + str(result)
    pickle.dump(result, open("strats/job_%d.strat" %i, "wb"))
    return util

# holes = pickle.load(open("2hand_groups_py2.cards"))
# communities = pickle.load(open("3hand_cleaned.group"))
jobWrapper(1000)
# pool = Pool(processes=4)
# print(pool.map(jobWrapper, list(range(4))))
# pool.close()
# pool.join()
