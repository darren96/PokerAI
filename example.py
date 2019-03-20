from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer

#TODO:config the config as our wish
config = setup_config(max_round=10, initial_stack=10000, small_blind_amount=10)



config.register_player(name="f1", algorithm=RandomPlayer())
config.register_player(name="FT2", algorithm=RaisedPlayer())


game_result = start_poker(config, verbose=1)

# verbose=0 because game progress is visualized by ConsolePlayer
# verbose=1 allows simple game logs to output after start_poker call
"""
If wish to participate in the game as a console player, check https://ishikota.github.io/PyPokerEngine/tutorial/participate_in_the_game/
"""