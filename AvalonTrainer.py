from Agent import AvalonPlayer
from Game import Avalon
import tensorflow as tf
import numpy as np

def train(players):
    player_losses = [None for p in players]

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

        for i, player in enumerate(players):
            player_losses[i] = player.loss_function(true_sides, true_merlin, result[i])

    for i, player in enumerate(players):
        loss = player_losses[i]
        gradients = tape.gradient(loss, player.model.trainable_variables)
        player.model.optimizer.apply_gradients(zip(gradients, player.model.trainable_variables))

    return np.mean(player_losses)



path = '/gpfs/main/home/aivanov6/course/cs1470/Final/AvalonAI/saved_model/AvalonAI_'
version = 1
path = path + str(version)

players = [AvalonPlayer() for i in range(5)]

for player in players:
    try:
        player.model.load_weights(path)
    except:
        pass

for i in range(100):
    loss = train(players)
    print("LOSS: ", loss)

players[0].model.save_weights(path)
