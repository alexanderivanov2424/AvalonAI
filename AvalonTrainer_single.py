from Agent import AvalonPlayer
from Game import Avalon
import tensorflow as tf
import numpy as np
from Player import *

import matplotlib.pyplot as plt



def train(players, i):

    player = players[0]

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

        if game.winning_side() == 1:
            game.guess_merlin()

        result = game.get_game_result()
        true_merlin = tf.constant(game.roles == 2, dtype="float32")
        true_sides = tf.constant(game.sides == 1, dtype="float32")


        loss = player.loss_function(true_sides, true_merlin, result[0])

    gradients = tape.gradient(loss, player.model.trainable_variables)
    player.model.optimizer.apply_gradients(zip(gradients, player.model.trainable_variables))

    for p in players:
        p.reset()

    return np.mean(loss)



path = './{}/AvalonAI'
version = "save_2"
new_version = "save_3"

players = [AvalonPlayer() for i in range(5)]

for player in players:
    try:
        player.model.load_weights(path.format(version))
    except:
        pass

player_to_train = np.random.randint(0,5)

L = []
L_mean = []
for i in range(500):
    loss = train(players,player_to_train)
    #print("LOSS: ", loss, end='\r')
    #if i % 10 == 0:
    #    print()
    L.append(loss)
    L_mean.append(np.mean(L[-100:]))
    plt.plot(L_mean)
    plt.plot(L)
    plt.draw()
    plt.pause(.001)
    plt.cla()

    if i % 1 == 0:
        print("SAVE")
        players[player_to_train].model.save_weights(path.format(new_version))
