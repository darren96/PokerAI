from utils import *
from effective_hand_strength import HandStrengthEval
import unittest


class TestUtilities(unittest.TestCase):
    def test_set_product(self):
        set1 = ["A", "B"]
        set2 = ["1", "2"]
        res = set_product(set1, set2)
        res = sorted(res)
        self.assertEqual(res, ["A1", "A2", "B1", "B2"])

    def test_combinations(self):
        res = get_all_combinations([1,2,3,4], 2)
        print(res)
        self.assertEqual(len(res), 6)
        res = set(res)
        self.assertEqual(len(res), 6)

class TestEffectiveHandStrengh(unittest.TestCase):

    def test_handStrength(self):
        hand_strength = HandStrengthEval()
        print(hand_strength.hand_strength(["CQ","CK"], []))

