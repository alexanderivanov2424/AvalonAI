from Agent import AvalonPlayer
from Game import Avalon
import tensorflow as tf
import numpy as np
from Player import *

path = '/gpfs/main/home/aivanov6/course/cs1470/Final/AvalonAI/saved_model/AvalonAI_'
version = 1
path = path + str(version)

players = [AvalonPlayer() for i in range(4)]

for player in players:
    try:
        player.model.load_weights(path)
    except:
        pass

players.append(HumanPlayer())

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
print(result)
