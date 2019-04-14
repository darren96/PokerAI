import matplotlib.pyplot as plt
from matplotlib.table import Table
# from cfr_v2 import CFR
import pickle


# cfr = CFR()
# ante = 1.0
# bet1 = 2.0
# bet2 = 8.0

# util = cfr.train(1000, ante, bet1, bet2)

label = ['-1G', '0G', '1G', '2G', '3G', '4G', '5G', '6G', '7G', '8G', '9G', 
        '10G', '11G', '12G', '13G', '14G', '15G', '16G', '17G']
rank_index_map = {'-1G': 0, '0G': 1, '1G': 2, '2G': 3,
'3G': 4, '4G': 5, '5G': 6,
'6G': 7, '7G': 8, '8G': 9,
'9G': 10, '10G': 11, '11G': 12, '12G': 13,
'13G': 14, '14G': 15, '15G': 16, '16G': 17,
'17G': 18}

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

def create_table(title, frequencies):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    tb = Table(ax, bbox=[0,0,1,1])

    nrows, ncols = 1, len(label)
    width, height = 1.0 / ncols, 1.0 / nrows

    # Add cells
    for hand, val in frequencies.items():
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
result = pickle.load(open("10_million_2hand.strat", "rb"))
for decision in sorted(result):
    table = create_table(decision, result[decision])

plt.show()
