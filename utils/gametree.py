from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards

from effective_hand_strength import HandEvaluator

def showdown_probability(hole_cards, community_cards):
    """
    Evaluate/Estimate probability of reaching a leaf node.
    :param hole_cards:
    :param community_cards:
    :return:
    """
    hs = HandEvaluator()
    if len(community_cards) == 5:
        return hs.eval_hand(hole_cards, community_cards)
    else:
        return estimate_hole_card_win_rate(nb_simulation = 1000,
                                           nb_player = 2,
                                           hole_card = gen_cards(hole_cards),
                                           community_card = gen_cards(community_cards))


MAX_DEPTH = 20
class PlayerNode:
    def __init__(self, amount, depth, bb_pos, raises, hole_cards, community_cards, street, pot):
        self.amount = amount
        self.pot = pot
        self.depth = depth + 1
        self.bb_pos = bb_pos
        self.raises = raises
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.street = street
        self.children = {}

    def add_call_child(self):
        if "call" not in self.children:


    def add_raise_child(self):
        if "raise" not in self.children:
            PlayerNode(self.amount-20, self.depth+1, 1-bb_pos, self.raises+1, self.hole_cards, self.community_cards, self.street, self.pot+20)

    def get_utilities(self):

        if self.depth > MAX_DEPTH:
            return showdown_probability(self.hole_cards, self.community_cards)

        if self.street == "pre-flop":
            pass

        elif self.street == ""
