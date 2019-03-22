from itertools import combinations

def set_product(set1, set2):
    res = []
    for i in set1:
        for j in set2:
            res.append(i+j)
    return res


def get_all_possible_cards():
    numbers = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
    suites = ["S", "D", "H", "C"]
    return set_product(suites, numbers)


def get_all_combinations(cards, n):
    return list(combinations(cards, n))