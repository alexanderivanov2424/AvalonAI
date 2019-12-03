from Agent import AvalonPlayer
from Game import Avalon
import tensorflow as tf

players = [AvalonPlayer() for i in range(5)]
game = Avalon(players)


def train():
    game.start_game()
    while not game.is_over():
        print("get team")
        game.get_team()
        print("vote team")
        game.vote_team()
        print("show team")
        game.show_team()
        if game.team_r:  # extracting vote result
            print("vote team")
            game.vote_quest()
            print("show team")
            game.show_quest()

    if game.winning_side() == 1:
        game.guess_merlin()

    result = game.get_game_result()
    true_merlin = tf.constant(game.roles == 2, dtype="float32")
    true_sides = tf.constant(game.sides == 1, dtype="float32")

    for i, player in enumerate(players):
        with tf.GradientTape() as tape:
            loss = player.loss_function(true_merlin, true_sides, result[i])
        gradients = tape.gradient(loss, player.model.trainable_variables)
        player.model.optimizer.apply_gradients(
            zip(gradients, player.model.trainable_variables)
        )


train()
