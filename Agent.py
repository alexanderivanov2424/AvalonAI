from Player import Player

import tensorflow as tf
import numpy as np
from tensorflow.compat.v2.keras import layers, Sequential

class Model(tf.keras.Model):
    def __init__(self, action_size):
        super(Model, self).__init__()

        self.action_size = action_size

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)


        self.GRU = layers.GRU(64,return_sequences=True,return_state=True, dtype='float32')

        self.P = Sequential()
        self.P.add(layers.Dense(200, activation="relu", dtype='float32'))
        self.P.add(layers.Dense(200, activation="relu", dtype='float32'))
        self.P.add(layers.Dense(self.action_size, activation="relu", dtype='float32'))

    def call(self, inputs, hidden):
        inputs = tf.dtypes.cast(np.array([[inputs]]), dtype='float32')
        inputs, *next_state = self.GRU(inputs,initial_state=hidden)
        inputs = self.P(inputs)
        return tf.reshape(inputs,(-1,)), next_state

    def loss(self, win):
        loss_array = tf.ones(1) - tf.constant(win, dtype='float32')
        return tf.reduce_mean(loss_array)

class AvalonPlayer(Player):

        def __init__(self):
            self.model = Model(17)
            self.hidden = None
            self.side_guess_list = []
            self.state_list = []
            pass

        def run_model(self, state):
            self.state_list.append(state)
            actions, self.hidden = self.model.call(state,self.hidden)
            self.side_guess.append(actions[12:17])
            return actions

        def see_start(self, state):
            #show player start state
            actions = self.run_model(state)

        def pick_team(self, state):
            #show player state
            #request for team to be selected
            actions = self.run_model(state)
            return actions[0:5]

        def vote_team(self, state):
            #inform player of proposed team
            #request for team vote
            actions = self.run_model(state)
            return actions[5] > .5


        def show_team(self, state):
            #inform player of selected team (or if no team picked)
            #show player who votes
            #no return
            actions = self.run_model(state)
            pass

        def vote_quest(self, state):
            #show who is on team
            #request for quest vote
            actions = self.run_model(state)
            return actions[6] > .5

        def see_quest(self, state):
            #show quest result
            #no return
            actions = self.run_model(state)
            pass

        def guess_merlin(self, state):
            #request guess for merlin
            actions = self.run_model(state)
            return actions[7:12]
