from math import ceil
from pypokerengine.engine.card import Card

# Do not use `Card.RANK_MAP.get(12)` as it would return the Card's character, e.g. 1,2,...10,J,Q,K,A
ACE = 14
KING = 13
QUEEN = 12
JACK = 12


class ChenFormula:
    """
    Implements Chen Formula as described by http://www.thepokerbank.com/strategy/basic/starting-hand-selection/chen-formula/
    It is used for scoring different STARTING (hole) hands only. This does not take into consideration of community cards.
    Note that this should only be used as a guideline as to whether to play your hand, where by the formula can help
    inform you what hands to play, but it can't tell you when to call, raise, or fold.
    For more info: https://poker.stackexchange.com/questions/2687/how-to-use-or-not-use-chen-formula-valuation-in-different-scenarios
    """

    def __init__(self):
        pass

    @staticmethod
    def score(our_starting_hand):
        """
        :param our_starting_hand: The 2 hole cards
        :return: score as integer
        """

        if len(our_starting_hand) != 2:
            raise Exception("Your starting hands must have 2 cards!")

        card_one_rank = Card.from_str(our_starting_hand[0]).rank
        card_one_suit = Card.from_str(our_starting_hand[0]).suit
        card_two_rank = Card.from_str(our_starting_hand[1]).rank
        card_two_suit = Card.from_str(our_starting_hand[1]).suit

        high_rank = max(card_one_rank, card_two_rank)
        low_rank = min(card_one_rank, card_two_rank)
        rank_difference = high_rank - low_rank
        gap_between_cards = rank_difference - 1 if rank_difference > 1 else 0
        is_pair = card_one_rank == card_two_rank
        is_suited = card_one_suit == card_two_suit

        if high_rank == ACE:
            score = 10.0
        elif high_rank == KING:
            score = 8.0
        elif high_rank == QUEEN:
            score = 7.0
        elif high_rank == JACK:
            score = 6.0
        else:
            score = high_rank / 2.0

        """
        If cards are a pair, multiply the score by 2. 
        If the resulting score is < 5.0, set score to 5.0 as the minimum score for a pair is 5.0.
        """
        if is_pair:
            score *= 2
            if score < 5.0:
                score = 5.0

        """
        If cards have the same suit, add 2 to the score.
        """
        if is_suited:
            score += 2.0

        """
        Update score based on gap between cards.
        E.g. 5 and 7 has a gap of 1, 5 and 6 has a gap of 0, 5 and 10 has a gap of 4.
        However, ACE is special in this case where it is considered to be 4 gaps or more.
        E.g. A and 2 has a gap of at least 4
        """
        if 1 <= gap_between_cards <= 2:
            score -= gap_between_cards
        elif gap_between_cards == 3:
            score -= 4.0
        elif gap_between_cards > 3:
            score -= 5.0

        """
        Add 1 point if there is 0 or 1 gap between cards, and both cards are lower than QUEEN".
        This does not apply to pair cards.       
        """
        if not is_pair and gap_between_cards <= 1 and card_one_rank < QUEEN and card_two_rank < QUEEN:
            score += 1.0

        return ceil(score)
