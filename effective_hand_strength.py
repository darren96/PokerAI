from pypokerengine.engine.card import Card
from pypokerengine.engine.hand_evaluator import HandEvaluator
from utils import get_all_possible_cards, get_all_combinations

BEHIND = 0
AHEAD = 1
TIE = 2


class HandStrengthEval:
    """
    Implements the Effective Hand Strength as described by https://en.wikipedia.org/wiki/Poker_Effective_Hand_Strength_(EHS)_algorithm
    """
    def __init__(self):
        """
        Compute all possible hands once before hand.
        """
        self.all_possible_hands = get_all_combinations(get_all_possible_cards(), 2)
        self.hand_evaluator = HandEvaluator()

    def rank(self, our_hand, board_cards):
        """
        A simple wrapper around the hand_evaluator in pypoker engine. Used to convert strings to cards
        :param our_hand: A list of strings containing the 2 cards in our hand
        :param board_cards: A list of strings containing 0 to 5 cards on the board
        :return: rank as integer
        """
        hand_deck = list(map(Card.from_str, our_hand))
        cards = list(map(Card.from_str, board_cards))
        return self.hand_evaluator.eval_hand(hand_deck, cards)

    def hand_strength(self, our_hand, board_cards):
        """
        Evaluates the hand strength i.e P(winning| cards in hand and cards on board) + 0.5*P(tie| cards in hand
        and cards on board). Executes pretty fast (within real time)
        :param our_hand: The cards in our hand. Must be a list of 2 strings
        :param board_cards: The cards on the board. Can be list of length 0 to 5 of strings.
        :return: hand strength as float
        """
        ahead = tied = behind = 0

        our_rank = self.rank(our_hand, board_cards)
        for hand in self.all_possible_hands:
            if hand[0] in our_hand + board_cards or hand[1] in our_hand + board_cards:
                continue

            opp_rank = self.rank(hand, board_cards)
            if our_rank > opp_rank:
                ahead += 1
            elif our_rank == opp_rank:
                tied += 1
            else:
                behind += 1

        return (ahead + tied / 2) / (ahead + tied + behind)

    def get_possible_final_boards(self, our_hand, board_cards):
        """
        Given the cards on the table return possible configurations for the final board
        :param our_hand:
        :param board_cards:
        :return:
        """
        cards_in_deck = filter(lambda x: x not in our_hand and x not in board_cards, get_all_possible_cards())
        return get_all_combinations(cards_in_deck, 5-len(board_cards))

    def hand_potential(self, our_hand, board_cards):
        """
        Calculates the potential that the deck will lead to an improvement in our hand's potential or a detorioration.
        Very Slow...
        :param our_hand: The cards in our hand. Must be a list of 2 strings
        :param board_cards:  The cards on the board. Can be list of length 0 to 5 of strings.
        :return: Tuple of format (Ppot, Npot) where Ppot is the chance that the cards will improve and Npot is the
        chance that the cards will get worse.
        """
        HP = [[0]*3 for i in range(3)]
        HPTotal = [0]*3
        our_rank = self.rank(our_hand, board_cards)
        for opponent_hand in self.all_possible_hands:
            if opponent_hand[0] in our_hand + board_cards or opponent_hand[1] in our_hand + board_cards:
                continue

            opp_rank = self.rank(opponent_hand, board_cards)

            if our_rank > opp_rank: index = AHEAD
            elif our_rank == opp_rank: index = TIE
            else: index = BEHIND
            HPTotal[index] += 1

            for additional in self.get_possible_final_boards(our_hand, board_cards):
                board = board_cards + list(additional)
                our_best = self.rank(our_hand, board_cards)
                opp_best = self.rank(opponent_hand, board)
                if our_best > opp_best: HP[index][AHEAD] += 1
                elif our_best == opp_best: HP[index][TIE] += 1
                else: HP[index][BEHIND] += 1

        Ppot = (HP[BEHIND][AHEAD] + HP[BEHIND][TIE] / 2 + HP[TIE][AHEAD] / 2) / (HPTotal[BEHIND] + HPTotal[TIE])
        Npot = (HP[AHEAD][BEHIND] + HP[TIE][AHEAD] / 2 + HP[AHEAD][TIE] / 2) / (HPTotal[AHEAD] + HPTotal[TIE])
        return Ppot, Npot

