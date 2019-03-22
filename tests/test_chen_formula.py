from chen_formula import ChenFormula
import unittest

class TestChenFormula(unittest.TestCase):
    def test_chen_formula(self):
        hand_strength = ChenFormula()
        self.assertEqual(hand_strength.score(["SA", "SK"]), 12.0)
        self.assertEqual(hand_strength.score(["CT", "DT"]), 10.0)
        self.assertEqual(hand_strength.score(["H5", "H7"]), 6.0)
        self.assertEqual(hand_strength.score(["C2", "H7"]), -1.0)
        self.assertEqual(hand_strength.score(["CA", "HA"]), 20.0)
        self.assertEqual(hand_strength.score(["SA", "S2"]), 7.0)
        with self.assertRaises(Exception) as context:
            hand_strength.score(["SA"])
        self.assertTrue('Your starting hands must have 2 cards!' in context.exception)

if __name__ == '__main__':
    # Only run this tests if it's not imported as a module
    unittest.main()
