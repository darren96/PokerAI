from chen_formula import ChenFormula
import unittest


class TestChenFormula(unittest.TestCase):
    def setUp(self):
        self.hand_strength = ChenFormula()

    def test_chen_formula(self):
        self.assertEqual(self.hand_strength.score(["SA", "SK"]), 12.0)
        self.assertEqual(self.hand_strength.score(["CT", "DT"]), 10.0)
        self.assertEqual(self.hand_strength.score(["H5", "H7"]), 6.0)
        self.assertEqual(self.hand_strength.score(["C2", "H7"]), -1.0)
        self.assertEqual(self.hand_strength.score(["CA", "HA"]), 20.0)
        self.assertEqual(self.hand_strength.score(["SA", "S2"]), 7.0)
        self.assertEqual(self.hand_strength.score(["SJ", "S5"]), 3)
        self.assertEqual(self.hand_strength.score(["CQ", "D6"]), 2)

    def test_chen_formula_exception(self):
        with self.assertRaises(Exception) as error:
            self.hand_strength.score(["SA"])
        self.assertTrue('Your starting hands must have 2 cards!' in error.exception)
        with self.assertRaises(Exception) as error:
            self.hand_strength.score(["SA"])
        self.assertTrue('Your starting hands must have 2 cards!' in error.exception)
        with self.assertRaises(Exception) as error:
            self.hand_strength.score(["SA", "SA"])
        self.assertTrue('You cannot have 2 cards of the same rank and suite!' in error.exception)

    def tearDown(self):
        self.hand_strength = None


if __name__ == '__main__':
    # Only run this tests if it's not imported as a module
    unittest.main()
