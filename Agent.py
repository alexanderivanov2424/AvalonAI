from Player import Player

import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, losses, Sequential
from tensorflow.nn import sigmoid_cross_entropy_with_logits


class Model(tf.keras.Model):
    def __init__(self):
        super(Model, self).__init__()

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        self.GRU = layers.GRU(
            50, return_sequences=True, return_state=True, dtype="float32",
        )

        self.P = Sequential()
        self.P.add(layers.Dense(100,activation="relu", dtype="float32"))
        #self.P.add(layers.BatchNormalization())
        self.P.add(layers.Dense(100,activation="relu", dtype="float32",use_bias=False))
        #self.P.add(layers.BatchNormalization())
        #self.P.add(layers.Dense(100,activation="sigmoid", dtype="float32",use_bias=False))
        #self.P.add(layers.BatchNormalization())


        self.team_prop = layers.Dense(5, activation="softmax", dtype="float32", name="team_prop")

        self.team_vote = layers.Dense(2, activation="softmax", dtype="float32", name="team_vote")

        self.quest_vote = layers.Dense(2, activation="softmax", dtype="float32", name="quest_vote")

        self.merlin_guess = layers.Dense(5, activation="softmax", dtype="float32", name="merlin_guess")

        self.side_guess = layers.Dense(5, activation="softmax", dtype="float32", name="side_guess")

    def call(self, inputs, hidden,action):
        inputs = tf.dtypes.cast(np.array([[inputs]]), dtype="float32")
        inputs, *next_state = self.GRU(inputs, initial_state=hidden)
        if not action == "none":
            inputs = self.P(inputs)

        if action == "tp":
            inputs = self.team_prop(inputs)
        elif action == "tv":
            inputs = self.team_vote(inputs)
        elif action == "qv":
            inputs = self.quest_vote(inputs)
        elif action == "mg":
            inputs = self.merlin_guess(inputs)
        elif action == "sg":
            inputs = self.side_guess(inputs)

        #print(inputs)
        return tf.squeeze(inputs), next_state


#     def loss(self, win):
#         loss_array = tf.ones(1) - tf.constant(win, dtype="float32")
#         return tf.reduce_mean(loss_array)

class AvalonPlayer(Player):
    def __init__(self):
        self.model = Model()
        self.hidden = None
        self.action_logit_list = []

    def run_model(self, state, action):
        actions, self.hidden = self.model.call(state, self.hidden, action)
        return actions

    def reset(self):
        self.action_logit_list = []
        self.hidden = None

    def loss_function(self, did_win):
        loss = 0
        reward = 100 if did_win else -100
        for action_logit in reversed(self.action_logit_list):
            loss += -tf.reduce_sum(tf.math.log(.001 + tf.cast(action_logit,tf.float32)) * reward)
            reward *= 0.99
        return loss

    def see_start(self, state):
        # show player start state
        actions = self.run_model(state,"none")

    def pick_team(self, state, team_size):
        # show player state
        # request for team to be selected
        actions = self.run_model(state,"tp")
        on_team = np.random.choice(5,team_size,replace=False,p=np.array(actions))

        self.action_logit_list.append(tf.gather(actions,on_team))
        team = np.zeros(5)
        team[on_team] = 1
        return team

    def vote_team(self, state):
        # inform player of proposed team
        # request for team vote
        actions = self.run_model(state,"tv")
        vote = int(actions[0] < np.random.rand())
        V = np.array(vote)
        self.action_logit_list.append(tf.gather(actions,V))
        return vote

    def show_team(self, state):
        # inform player of selected team (or if no team picked)
        # show player who votes
        # no return
        actions = self.run_model(state,"none")

    def vote_quest(self, state):
        # show who is on team
        # request for quest vote
        actions = self.run_model(state,"qv")
        vote = int(actions[0] < np.random.rand())
        V = np.array(vote)
        self.action_logit_list.append(tf.gather(actions,V))
        return vote

    def see_quest(self, state):
        # show quest result
        # no return
        actions = self.run_model(state,"none")
        self.action_logit_list.append(1)

    def guess_merlin(self, state):
        # request guess for merlin
        actions = self.run_model(state,"mg")
        #print("$$$MERLIN$$$ ",np.array(actions))
        M = np.random.choice(5,p=np.array(actions))
        self.action_logit_list.append(tf.gather(actions,M))
        pick = np.zeros(5)
        pick[M] = 1
        return pick
