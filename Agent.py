from Player import Player

import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, losses, Sequential
from tensorflow.nn import sigmoid_cross_entropy_with_logits


class Model(tf.keras.Model):
    def __init__(self, action_size):
        super(Model, self).__init__()

        self.action_size = action_size

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        self.GRU = layers.GRU(
            1, return_sequences=True, return_state=True, dtype="float32",
        )

        self.P = Sequential()
        self.P.add(layers.Dense(100,activation="relu", dtype="float32",use_bias=False))
        self.P.add(layers.BatchNormalization())
        self.P.add(layers.Dense(100,activation="relu", dtype="float32",use_bias=False))
        self.P.add(layers.BatchNormalization())
        self.P.add(layers.Dense(100,activation="relu", dtype="float32",use_bias=False))
        self.P.add(layers.BatchNormalization())
        self.P.add(layers.Dense(self.action_size, activation="sigmoid", dtype="float32"))

    def call(self, inputs, hidden):
        inputs = tf.dtypes.cast(np.array([[inputs]]), dtype="float32")
        inputs, *next_state = self.GRU(inputs, initial_state=hidden)
        inputs = self.P(inputs)
        return tf.squeeze(inputs), next_state


#     def loss(self, win):
#         loss_array = tf.ones(1) - tf.constant(win, dtype="float32")
#         return tf.reduce_mean(loss_array)


class AvalonPlayer(Player):
    def __init__(self):
        self.model = Model(17)
        self.hidden = None
        self.merlin_guess_list = []
        self.side_guess_list = []
        self.action_logit_list = []

        self.proposed_team_mask = tf.convert_to_tensor([1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],dtype='float32')
        self.team_vote_mask =     tf.convert_to_tensor([0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],dtype='float32')
        self.quest_vote_mask =    tf.convert_to_tensor([0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],dtype='float32')
        self.merlin_guess_mask =  tf.convert_to_tensor([0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],dtype='float32')
        self.side_guess_mask =    tf.convert_to_tensor([0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],dtype='float32')

    def run_model(self, state):
        actions, self.hidden = self.model.call(state, self.hidden)
        self.merlin_guess_list.append(actions * self.merlin_guess_mask)
        self.side_guess_list.append(actions * self.side_guess_mask)
        return actions

    def reset(self):
        self.merlin_guess_list = []
        self.side_guess_list = []
        self.action_logit_list = []
        self.hidden = None

    def loss_function(self, true_sides, true_merlin, did_win):
        true_merlin = tf.concat([tf.zeros(7),true_merlin,tf.zeros(5)], 0)
        true_sides = tf.concat([tf.zeros(12),true_sides], 0)
        loss = 0
        reward = 10 if did_win else -10
        for action_logit in reversed(self.action_logit_list):
            diff = action_logit - 0.5
            loss += -diff * diff * reward
            reward *= 0.99
        # for guess in self.merlin_guess_list:
        #     loss += sigmoid_cross_entropy_with_logits(true_merlin, guess)
        # for guess in self.side_guess_list:
        #     loss += sigmoid_cross_entropy_with_logits(true_sides, guess)
        return loss + reward

    def see_start(self, state):
        # show player start state
        actions = self.run_model(state)
        self.action_logit_list.append(1)

    def pick_team(self, state):
        # show player state
        # request for team to be selected
        actions = self.run_model(state)
        self.action_logit_list.append(actions * self.proposed_team_mask)
        return np.array(actions[0:5]) > np.random.uniform(size=5)

    def vote_team(self, state):
        # inform player of proposed team
        # request for team vote
        actions = self.run_model(state)
        self.action_logit_list.append(actions * self.team_vote_mask)
        return actions[5] > np.random.uniform()

    def show_team(self, state):
        # inform player of selected team (or if no team picked)
        # show player who votes
        # no return
        actions = self.run_model(state)
        self.action_logit_list.append(1)

    def vote_quest(self, state):
        # show who is on team
        # request for quest vote
        actions = self.run_model(state)
        self.action_logit_list.append(actions * self.quest_vote_mask)
        return actions[6] > np.random.uniform()

    def see_quest(self, state):
        # show quest result
        # no return
        actions = self.run_model(state)
        self.action_logit_list.append(1)

    def guess_merlin(self, state):
        # request guess for merlin
        actions = self.run_model(state)
        return np.array(actions[7:12]) > np.random.uniform(size=5)
