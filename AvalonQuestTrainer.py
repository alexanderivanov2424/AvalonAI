from Agent import AvalonPlayer
from Game import Avalon
from Player import *
import tensorflow as tf
import numpy as np

import matplotlib.pyplot as plt


def train(players):
    player_losses = [[] for p in players if not isinstance(p, HumanPlayer)]

    with tf.GradientTape(persistent=True) as tape:
        game = Avalon(players)
        game.start_game()
        while not game.is_over():
            game.get_team()
            game.vote_team()
            game.show_team()
            if game.team_r:  # extracting vote result
                game.vote_quest()
                game.show_quest()
                #get loss by quest
                quest_result = game.quests[game.current_quest-1]
                for i, player in enumerate(players):
                    if isinstance(player, HumanPlayer):
                        continue
                    player_losses[i].append(player.loss_quest(game.sides[i] == quest_result))

        if game.winning_side() == 1:
            game.guess_merlin()

        result = game.get_game_result()
        true_merlin = tf.constant(game.roles == 2, dtype="float32")
        true_sides = tf.constant(game.sides == 1, dtype="float32")

        print("#"*10)
        print(result)
        print(game.roles)
        print("#"*10)

        for i, player in enumerate(players):
            if isinstance(player, HumanPlayer):
                continue
            player_losses[i].append(player.loss_function(true_sides, true_merlin, result[i]))

    for i, player in enumerate(players):
        if isinstance(player,HumanPlayer):
            continue
        for loss in player_losses[i]:
            gradients = tape.gradient(loss, player.model.trainable_variables)
            player.model.optimizer.apply_gradients(
                zip(gradients, player.model.trainable_variables)
            )
        player.reset()

    return np.mean(player_losses)


path = "./{}/AvalonAI"
version = "save_quest_loss"
new_version = "save_quest_loss_human_trained"

players = [AvalonPlayer() for i in range(4)]

for player in players:
    try:
        player.model.load_weights(path.format(version))
    except:
        pass

players.append(HumanPlayer())

L = []
L_mean = []
for i in range(1000):
    loss = train(players)
    # print("LOSS: ", loss, end='\r')
    # if i % 10 == 0:
    #    print()
    L.append(loss)
    L_mean.append(np.mean(L[-100:]))
    plt.plot(L_mean)
    plt.plot(L)
    plt.draw()
    plt.pause(0.001)
    plt.cla()

    if i % 1 == 0:
        print("SAVE")
        players[np.random.randint(0, 4)].model.save_weights(path.format(new_version))
        for player in players:
            if isinstance(player,HumanPlayer):
                continue
            try:
                player.model.load_weights(path.format(new_version))
            except:
                pass
