from Agent import AvalonPlayer
from Game import Avalon
import tensorflow as tf
import numpy as np
from Player import *

path = "./{}/AvalonAI"
version = "final_training(full,sp_net)"
path = path.format(version)

players = [AvalonPlayer() for i in range(5)]

for player in players:
    try:
        player.model.load_weights(path)
    except:
        pass


#players.append(RandomPlayer())


wins = 0
good_team_win = 0
win_and_good = 0
merlin_guess = 0

for i in range(1000):
    print(i,end='\r')
    game = Avalon(players)
    game.start_game()
    while not game.is_over():
        game.get_team()
        game.vote_team()
        game.show_team()
        if game.team_r:  # extracting vote result
            game.vote_quest()
            game.show_quest()

    if game.winning_side() == 1:
        game.guess_merlin()

    result = game.get_game_result()
    good_team_win += np.sum(result) == 3
    merlin_guess += game.merlin_discovered

    I = 4
    win_and_good += result[I] and game.sides[I] == 1
    wins+=result[I]
    #print([players[-1].role_to_name(r) for r in game.roles])
print()
print("WINS:", wins)
print("GOOD TEAM WINS:", good_team_win)
print("WIN WHEN GOOD:", win_and_good)
print("WIN WHEN BAD:", wins-win_and_good)
print("GUESSED MERLIN", merlin_guess)

"""
type                win %       %GOOD WIN
4 AI vs RANDOM      .545

4 AI vs AI          .449        32.5
4 RANDOM vs RANDOM  .4          0
4 RANDOM vs AI      .395        0
#################################
4 AI vs RANDOM
WINS: 471
GOOD TEAM WINS: 142
WIN WHEN GOOD: 112
WIN WHEN BAD: 359
GUESSED MERLIN 28
#################################
4 AI vs AI
WINS: 512
GOOD TEAM WINS: 388
WIN WHEN GOOD: 258
WIN WHEN BAD: 254
GUESSED MERLIN 97
#################################
4 RANDOM vs RANDOM
WINS: 386
GOOD TEAM WINS: 0
WIN WHEN GOOD: 0
WIN WHEN BAD: 386
GUESSED MERLIN 0
#################################
4 RANDOM vs AI
WINS: 399
GOOD TEAM WINS: 0
WIN WHEN GOOD: 0
WIN WHEN BAD: 399
GUESSED MERLIN 0
#################################
"""
