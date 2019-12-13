import logging, os

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from Agent import AvalonPlayer
from Game import Avalon
from Player import *
import tensorflow as tf
import numpy as np


def train(players):
    # loss stored in a list for each player
    # this allows for example, getting the loss after every quest
    # as well as the loss at the end of the game (aka for reward shaping)
    player_losses = [[] for p in players if not isinstance(p, HumanPlayer)]

    with tf.GradientTape(persistent=True) as tape:

        # Game Simulation
        game = Avalon(players)
        game.start_game()
        while not game.is_over():
            game.get_team()
            leader_on_quest += game.team[game.leader]

            game.vote_team()
            game.show_team()
            if game.team_r:  # extracting vote result
                game.vote_quest()
                game.show_quest()

        if game.winning_side() == 1:
            game.guess_merlin()

        # extract game result for each player
        result = game.get_game_result()

        # calculating loss for each player given the game results.
        for i, player in enumerate(players):
            player_losses[i].append(player.loss_function(result[i]))

    # perform gradient step for all players
    for i, player in enumerate(players):
        for loss in player_losses[i]:
            gradients = tape.gradient(loss, player.model.trainable_variables)
            player.model.optimizer.apply_gradients(
                zip(gradients, player.model.trainable_variables)
            )
        player.reset()

    return np.mean(player_losses)


path = "./{}/AvalonAI"
version = "save_weights"
new_version = "save_weights"

players = [AvalonPlayer() for i in range(5)]

for player in players:
    try:
        player.model.load_weights(path.format(version))
    except:
        pass


for i in range(10000):
    loss = train(players)

    if i % 50 == 0:
        print()
        print("SAVE")
        for player in players:
            vars = [v for v in player.model.trainable_variables if "quest_vote" in v.name or "merlin_guess" in v.name]
            if len(vars) == 2:
                player.model.save_weights(path.format(new_version))
                break

        for player in players:
            player.model.load_weights(path.format(new_version))
