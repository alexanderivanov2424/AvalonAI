import logging, os

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from Agent import AvalonPlayer
from Game import Avalon
from Player import *
import tensorflow as tf
import numpy as np

import matplotlib.pyplot as plt

leader_on_quest_list = []
double_fail_list = []
team_rejects_list = []



def train(players):
    player_losses = [[] for p in players if not isinstance(p, HumanPlayer)]

    leader_on_quest = 0
    double_fail = 0
    team_rejects = 0

    with tf.GradientTape(persistent=True) as tape:
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
                double_fail += game.quest_fail_votes == 2
                #get loss by quest
                quest_result = game.quests[game.current_quest-1]
                for i, player in enumerate(players):
                    #player_losses[i].append(player.loss_quest(game.sides[i] == quest_result))
                    pass
            else:
                team_rejects += 1

        if game.winning_side() == 1:
            game.guess_merlin()

        result = game.get_game_result()
        true_merlin = tf.constant(game.roles == 2, dtype="float32")
        true_sides = tf.constant(game.sides == 1, dtype="float32")

        team_rejects / (game.current_quest + 1)
        #if np.sum(result) == 3:
        print(game.quests)

        for i, player in enumerate(players):
            player_losses[i].append(player.loss_function(true_sides, true_merlin, result[i]))

    for i, player in enumerate(players):
        for loss in player_losses[i]:
            gradients = tape.gradient(loss, player.model.trainable_variables)
            player.model.optimizer.apply_gradients(
                zip(gradients, player.model.trainable_variables)
            )
        player.reset()

    leader_on_quest_list.append(leader_on_quest)
    double_fail_list.append(double_fail)
    team_rejects_list.append(team_rejects)
    return np.mean(player_losses)


path = "./{}/AvalonAI"
version = "final"
new_version = "final"

players = [AvalonPlayer() for i in range(5)]

for player in players:
    try:
        player.model.load_weights(path.format(version))
    except:
        pass



for i in range(10000):
    loss = train(players)
    # print("LOSS: ", loss, end='\r')
    # if i % 10 == 0:
    #    print()

    plt.plot(leader_on_quest_list[-50:],label="leader on own quest per game")
    plt.plot(double_fail_list[-50:],label="double fails per game")
    plt.plot(team_rejects_list[-50:],label="team rejects per game")

    plt.draw()
    plt.legend()
    plt.pause(0.001)
    plt.cla()

    if i % 50 == 0:
        print("SAVE")
        for player in players:
            vars = [v for v in player.model.trainable_variables if "quest_vote" in v.name or "merlin_guess" in v.name]
            if len(vars) == 2:
                player.model.save_weights(path.format(new_version))
                break

        for player in players:
            player.model.load_weights(path.format(new_version))
