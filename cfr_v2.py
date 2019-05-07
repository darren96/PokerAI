import random
from pypokerengine.utils.card_utils import gen_deck
from pypokerengine.engine.card import Card
from pypokerengine.engine.hand_evaluator import HandEvaluator
import pprint as pp
import pickle

class Game:
    def __init__(self):
        pass

    RAISE = '0'
    CALL = '1'
    FOLD = '2'

    DECK = gen_deck()

    @staticmethod
    def deal_cards():
        sample = random.sample(Game.DECK.deck, 4)
        player_one_cards = sample[0:2]
        player_two_cards = sample[2:4]

        # print "P1 Card 1: %s " % player_one_cards[0]
        # print "P1 Card 2: %s " % player_one_cards[1]
        # print "P2 Card 3: %s" % player_two_cards[0]
        # print "P2 Card 4: %s" % player_two_cards[1]

        return player_one_cards, player_two_cards

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

# game = Game()
# p1c, p2c = game.deal_cards()
# game.get_higher_rank(11, 12)

class CFR:
    def __init__(self):
        self.game_states_ = dict()  # maps history to node

    @staticmethod
    def simplify_hand(hand, community_cards=None):
        """ Takes a hand (array of size two) and compresses the hand into simpler representation
            Also puts higher card in front
            i.e. Th 9h becomes T9s as both cards share the same suit
                Th 9s becomes T9o as both cards do not share the same suit (off-suit)
                Th Ts becomes TT (pair of tens)
        """
        card1 = hand[0]
        card2 = hand[1]

        key1 = "('%s', '%s')" %(card1, card2)
        key2 = "('%s', '%s')" %(card2, card1)

        if key1 in holes:
            hand = "%dG" %holes[key1]
        elif key2 in holes:
            hand = "%dG" %holes[key2]
        
        # if community_cards != None:
        #     for i in range(0, 2):
        #         community1 = community_cards[hand][0] if i != 0 else community_cards[hand][1]
        #         community2 = community_cards[hand][1] if i != 0 or 1 else community_cards[hand][2]
        #         key1 = "('%s', '%s', '%s')" %(community[i], community1, community2)
        #         key2 = "('%s', '%s', '%s')" %(community[i], community2, community1)
        #     if key1 in communities:
        #         hand = "%dG" %communities[key1]
        #     elif key2 in communities:
        #         hand = "%dG" %communities[key2]

        return hand

    @staticmethod
    def get_winner(hand1, hand2):
        hand_evaluator = HandEvaluator()
        lala = [str(hand1[0]), str(hand1[1])]
        # print "P1 hand %s" % lala
        lolo = [str(hand2[0]), str(hand2[1])]
        # print "P2 hand %s" % lolo
        community_cards = list(map(Card.from_str, [])) # empty for now, we assume community card is same for both

        p1_handdeck = list(map(Card.from_str, lala))
        p2_handdeck = list(map(Card.from_str, lolo))

        p1_hand = hand_evaluator.eval_hand(p1_handdeck, community_cards)
        p2_hand = hand_evaluator.eval_hand(p2_handdeck, community_cards)

        # print "P1 hand evaluate score %s" % p1_hand
        # print "P2 hand evaluate score %s" % p2_hand

        """ Gets the winner between the two hands
            Evaluated by PyPokerEngine la...
            returns 1 if the first hand wins
            returns 2 if the second hand wins
            returns 0 if the hands are tied
        """

        if p1_hand > p2_hand:
            return 1
        elif p2_hand > p1_hand:
            return 2
        elif p1_hand == p2_hand:
            return 0

    def train(self, iterations, ante=1.0, bet1=2.0, bet2=8.0, print_interval=1000000):
        """ Do ficticious self-play to find optimal strategy"""
        util = 0.0

        self.ante = ante
        self.bet1 = bet1
        self.bet2 = bet2

        # print "Ante: %f   Bet-1: %f   Bet-2: %f" % (ante, bet1, bet2)

        for i in range(iterations):
            if i % print_interval == 0 and i != 0:
                print "P1 expected value after %i iterations: %f" % (i, util / i)

            player_one_cards, player_two_cards = Game.deal_cards()
            p1_hand = self.simplify_hand(player_one_cards)
            p2_hand = self.simplify_hand(player_two_cards)
            # print "p1_hand: %s" %(p1_hand)
            # print "p2_hand: %s" %(p2_hand)
            # cards = [p1_hand, p2_hand]
            cards = [player_one_cards, player_two_cards]
            history = list()
            util += self.cfr(cards, history, 1, 1)

        return util / iterations

    def get_strategy(self):
        result = dict()
        p1_bet = 'Player One Betting Range'
        p1_bet_call = 'Player One Call All-in Range'
        p1_check_call = 'Player One Check-Call Range'
        p1_check_raise = 'Player One Check-Raise All-in Range'

        p2_call = 'Player Two Calling Range'
        p2_raise = 'Player Two All-in Range'
        p2_bet = 'Player Two Betting Range'
        p2_bet_call = 'Player Two Call All-in Range'

        result[p1_bet] = dict()
        result[p1_bet_call] = dict()
        result[p1_check_raise] = dict()
        result[p1_check_call] = dict()

        result[p2_call] = dict()
        result[p2_raise] = dict()
        result[p2_bet] = dict()
        result[p2_bet_call] = dict()

        for state, node in self.game_states_.items():
            # hand = state[0:2] if state[0] == state[1] else state[0:3]
            hand = state[0:2] if state[1] == "G" else state[0:3]
            # print "Hand: %s" % hand
            history = state[2:] if len(hand) == 2 else state[3:]
            # history = state[4:]
            print "hand: %s \nhistory: %s" %(hand, history)

            # player 1
            if len(history) == 0:
                result[p1_bet][hand] = node.strategy_[Game.RAISE]
            # player 2
            elif len(history) == 1:
                result[p2_raise][hand] = node.strategy_[Game.RAISE]
                result[p2_call][hand] = node.strategy_[Game.CALL]
            # player 1
            elif len(history) == 2:
                if history[0] == Game.RAISE:
                    result[p1_bet_call][hand] = node.strategy_[Game.CALL]
                else:
                    result[p1_check_raise][hand] = node.strategy_[Game.RAISE]
                    result[p1_check_call][hand] = node.strategy_[Game.CALL]
            # player 2
            elif len(history) == 3:
                result[p2_bet_call][hand] = node.strategy_[Game.CALL]

        # clean graphs
        tol = 0.005
        for hand, frequency in result[p1_bet].items():
            if frequency > 1 - tol and hand in result[p1_check_raise]:
                result[p1_check_raise][hand] = 0.0
            if frequency > 1 - tol and hand in result[p1_check_call]:
                result[p1_check_call][hand] = 0.0
            if frequency < tol and hand in result[p1_bet_call]:
                result[p1_bet_call][hand] = 0.0
        for hand, frequency in result[p2_bet].items():
            if frequency < tol and hand in result[p2_bet_call]:
                result[p2_bet_call][hand] = 0.0

        return result

    # @cards - the cards the players have, with index 0 being the card that player one has
    # and index 1 being the card that player two has
    # @history - a list of moves used to reach this game state
    # @probability1 - the probability of reaching this game state for player 1
    # @probability2 - the probability of reaching this game state for player 2
    def cfr(self, cards, history, probability1, probability2):

        num_moves = len(history)
        player = num_moves % 2
        opponent = 1 - player
        player_hand = cards[player]
        opponent_hand = cards[opponent]

        # print "=========== PLAYER " + str(player) + " TURN ==============="
        # print "history: " + str(history)
        # print "player_hand: %s %s" % (str(player_hand[0]), str(player_hand[1]))
        # print "opp_hand: %s %s" % (str(opponent_hand[0]), str(opponent_hand[1]))

        probability_weight = probability1 if player == 0 else probability2

        # print "probability_weight: " + str(probability_weight)
        # print "num_moves: " + str(num_moves)
        if num_moves >= 1:
            # Opponent folded
            if history[-1] == Game.FOLD:
                num_bets = 0
                for action in history:
                    if action == Game.RAISE:
                        num_bets += 1

                if num_bets == 2:
                    # print "Opponent folded, Player " + str(player) + " won " + str(self.ante + self.bet1)
                    return self.ante + self.bet1

                return self.ante
            # Opponent called a bet
            if history[-1] == Game.CALL:

                winner = self.get_winner(player_hand, opponent_hand)

                if winner == 0:
                    # print "Player " + str(player) + " calls the bet and lost"
                    return 0

                reward = self.ante
                num_bets = 0
                for action in history:
                    if action == Game.RAISE:
                        num_bets += 1
                if num_bets == 2:
                    reward += self.bet2
                elif num_bets == 1:
                    reward += self.bet1

                # print "Player " + str(player) + " calls the bet and won " + str(reward)
                return reward if winner == 1 else -reward
        
        # state = str(player_hand)
        p_hand = self.simplify_hand(player_hand)
        state = str(p_hand)

        for action in history:
            state += action

        # print "state: %s" % str(state)

        if state in self.game_states_:
            node = self.game_states_[state]  # Get our node if it already exists
            possible_actions = node.actions_
        else:
            # Create new Node with possible actions we can perform

            # print "state is not inside game tree"
            if len(history) == 0:
                possible_actions = [Game.CALL, Game.RAISE]
            else:
                if history[-1] == Game.RAISE:
                    possible_actions = [Game.CALL, Game.FOLD]
                    num_bets = 0
                    for action in history:
                        if action == Game.RAISE:
                            num_bets += 1
                    if num_bets == 1:
                        possible_actions.append(Game.RAISE)
                else:
                    possible_actions = [Game.CALL, Game.RAISE]

            nodce = Node(possible_actions)

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

            if player == 0:
                util[action] = -self.cfr(cards, next_history, probability1 * strategy[action], probability2)
            else:
                util[action] = -self.cfr(cards, next_history, probability1, probability2 * strategy[action])

            node_util += strategy[action] * util[action]

        # compute regret and update Game State for the node based on utility of all actions
        for action in possible_actions:
            regret = util[action] - node_util
            if player == 0:
                node.regret_sum_[action] += regret * probability2
            else:
                node.regret_sum_[action] += regret * probability1

        # print "node_util: " + str(node_util)

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

ante = 5.0
bet1 = 10.0
bet2 = 20.0
holes = pickle.load(open("2hand_groups_py2.cards"))
# communities = pickle.load(open("../3hand_cleaned.group"))
util = cfr.train(10000000, ante, bet1, bet2)
print "Player One Expected Value Per Hand: %f" % util
result = cfr.get_strategy()
# print "Final strategy: " + str(result)
pickle.dump(result, open("10_million_2hand.strat", "wb"))
