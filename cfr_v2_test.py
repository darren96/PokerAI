import matplotlib.pyplot as plt
from matplotlib.table import Table
# from cfr_v2 import CFR
import pickle


# cfr = CFR()
# ante = 1.0
# bet1 = 2.0
# bet2 = 8.0

# util = cfr.train(1000, ante, bet1, bet2)

ACTION_TO_HISTORY_MAPPING = {"fold": "0", "call": "1", "raise": "2", "small_blind": "3", "big_blind": "4", "ante": "5"}
HISTORY_TO_ACTION_MAPPING = {"0": "fold", "1": "call", "2": "raise", "3": "small_blind", "4": "big_blind", "5": "ante"}

label = ['-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
        '10', '11', '12', '13', '14', '15', '16', '17']
rank_index_map = {'-1': 0, '0': 1, '1': 2, '2': 3,
'3': 4, '4': 5, '5': 6,
'6': 7, '7': 8, '8': 9,
'9': 10, '10': 11, '11': 12, '12': 13,
'13': 14, '14': 15, '15': 16, '16': 17,
'17': 18}

def get_color(frequency):
    if frequency >= 0.9:
        return 'green'
    elif frequency >= 0.75:
        return 'yellowgreen'
    elif frequency >= 0.5:
        return 'yellow'
    elif frequency >= 0.25:
        return 'orange'
    elif frequency >= 0.05:
        return 'orangered'
    else:
        return 'red'

def filter_strategy(original_result):
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

    for state, node in original_result.items(): 
            split_state = state.split("G")
            if len(split_state) > 2:
                continue
            hand = split_state[0][1:]
            history = split_state[1] if len(split_state) == 2 else ""
            # print("hand: %s \nhistory: %s" %(hand, history))

            for i in range(len(history)):
                if i % 2 == 0:
                    print(history[i])
            # # player 1
            # if len(history) == 0:
            #     result[p1_bet][hand] = node[ACTION_TO_HISTORY_MAPPING["raise"]]
            # # player 2
            # elif len(history) == 1:
            #     result[p2_raise][hand] = node[ACTION_TO_HISTORY_MAPPING["raise"]]
            #     result[p2_call][hand] = node[ACTION_TO_HISTORY_MAPPING["call"]]
            # # player 1
            # elif len(history) == 2:
            #     if history[0] == ACTION_TO_HISTORY_MAPPING["raise"]:
            #         result[p1_bet_call][hand] = node[ACTION_TO_HISTORY_MAPPING["call"]]
            #     else:
            #         result[p1_check_raise][hand] = node[ACTION_TO_HISTORY_MAPPING["raise"]]
            #         result[p1_check_call][hand] = node[ACTION_TO_HISTORY_MAPPING["call"]]
            # # player 2
            # elif len(history) == 3:
            #     result[p2_bet_call][hand] = node[ACTION_TO_HISTORY_MAPPING["call"]]

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

def create_table(title, frequencies):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    tb = Table(ax, bbox=[0,0,1,1])

    nrows, ncols = 1, len(label)
    width, height = 1.0 / ncols, 1.0 / nrows

    # Add cells
    for hand, val in frequencies.items():
        # print(hand)
        # print(val)
        i = rank_index_map[hand]

        color = get_color(val)

        value_formatted = '{0:.2f}'.format(val)
        tb.add_cell(i + 1, 0, width, height, text=hand,
                    loc='center', facecolor=color)

    # Row Labels...
    for i in range(len(label)):
        tb.add_cell(i + 1, -1, width, height, text=label[i], loc='right',
                    edgecolor='none', facecolor='none')
    # Column Labels...
    # for j in range(len(label)):
    #     tb.add_cell(0, j, width, height/2, text=label[j], loc='center',
    #                        edgecolor='none', facecolor='none')
    ax.add_table(tb)
    plt.title(title)
    return fig


# print "Player One Expected Value Per Hand: %f" % util

# result = cfr.get_strategy()
result = pickle.load(open("strats/no_fold_cfr.strat", "rb"))
# print(result)
filtered_result = filter_strategy(result)
# for decision in sorted(result):
#     table = create_table(decision, filtered_result[decision])

plt.show()
