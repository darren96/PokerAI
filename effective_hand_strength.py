"""
Effective hand strength
HandStrength(ourcards, boardcards) {

    ahead = tied = behind = 0
    ourrank = Rank(ourcards, boardcards)
    for each case(oppcards) {

        opprank = Rank(oppcards, boardcards)
        if (ourrank>opprank) ahead += 1
        else if (ourrank==opprank) tied += 1
        else behind += 1

    }
    handstrength=(ahead+tied/2)/(ahead+tied+behind)
    return(handstrength)

}
https://stackoverflow.com/questions/111928/is-there-a-printf-converter-to-print-in-binary-format
 HandPotential(ourcards,boardcards){ // Hand potential array, each index represents ahead, tied, and behind.

    integer array HP[3][3] //initialize to 0
    integer array HPTotal[3] //initialize to 0
    ourrank = Rank(ourcards,boardcards)
    //Consider all two card combinations of the remaining cards for the opponent.
    for each case(oppcards){

        opprank = Rank(oppcards,boardcards)
        if(ourrank>opprank) index = ahead
        else if(ourrank=opprank) index = tied
        else index = behind
        HPTotal[index] += 1
        // All possible board cards to come.
        for each case(turn,river){ //Final 5-card board

            board = [boardcards,turn,river]
            ourbest = Rank(ourcards,board)
            oppbest = Rank(oppcards,board)
            if(ourbest>oppbest) HP[index][ahead]+=1
            else if(ourbest=oppbest) HP[index][tied]+=1
            else HP[index][behind]+=1

        }

    }
    //Ppot: were behind but moved ahead.
    Ppot = (HP[behind][ahead]+HP[behind][tied]/2+HP[tied][ahead]/2)/(HPTotal[behind]+HPTotal[tied])
    //Npot: were ahead but fell behind.
    Npot = (HP[ahead][behind]+HP[tied][behind]/2+HP[ahead][tied]/2)/(HPTotal[ahead]+HPTotal[tied])
    return(Ppot,Npot)

}
"""
from pypokerengine.engine.card import Card
from pypokerengine.engine.hand_evaluator import HandEvaluator
from utils import get_all_possible_cards, get_all_combinations

BEHIND = 0
AHEAD = 1
TIE = 2

class HandStrengthEval:
    def __init__(self):
        self.all_possible_hands = get_all_combinations(get_all_possible_cards(), 2)
        print(get_all_possible_cards())
        self.hand_evaluator = HandEvaluator()

    def rank(self, our_hand, board_cards):
        hand_deck = list(map(Card.from_str, our_hand))
        cards = list(map(Card.from_str, board_cards))
        return self.hand_evaluator.eval_hand(hand_deck, cards)

    def hand_strength(self, our_hand, board_cards):
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
        cards_in_deck = filter(lambda x: x not in our_hand and x not in board_cards, get_all_possible_cards())
        return get_all_combinations(cards_in_deck, 5-len(board_cards))

    def hand_potential(self, our_hand, board_cards):
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

