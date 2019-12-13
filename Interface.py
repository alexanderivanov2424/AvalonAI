from Agent import AvalonPlayer
from Game import GameStateBuilder, GameState, Avalon
import tensorflow as tf
import numpy as np
from Player import *
from AvalonTypes import *


path = "./{}/AvalonAI"
version = "final"
path = path.format(version)

AI = AvalonPlayer()

AI.model.load_weights(path)

N = 5

state = np.zeros(50)
leader = 0
quests = np.zeros(5)
current_quest = 0

fail_votes_list = []
team_matrix = []
evil_probs = np.zeros(5)
evil_probs = .4

team_sizes = [2, 3, 2, 3, 3]


def rtos(role):
    if role == -1:
        return -1
    if role == 0:
        return 0
    if role == 1:
        return 1
    if role == 2:
        return 1


a = int(input("Start role? (-1 0 1 2): "))
if a == -1:
    state[0] = -1
if a == 1:
    state[0] = 1
if a == 2:
    state[0] = 2
state[0] = rtos(a)
state[1] = a

leader = int(input("Who is Leader? (i): "))

roles = input("Visible Roles? (-1 0 1 2): ").split(" ")
roles = np.array([int(r) for r in roles])
sides = np.array([rtos(r) for r in roles])


state[7:12] = sides
state[12:17] = roles
state[12 + leader] = 1
state[45:50] = evil_probs

state[2] = 1 if leader == 0 else 0

print("SHOWING START")
AI.see_start(state)

state[7:12] = np.zeros(5)
state[12:17] = np.zeros(5)
state[12:17] = np.zeros(5)

while True:
    input("CONTINUE")
    state[2] = 1 if leader == 4 else 0
    state[22:27] = quests
    state[42] = team_sizes[current_quest]
    state[45:50] = evil_probs

    if leader == 0:
        print("PROPOSE TEAM")
        state[12 + leader] = 1
        state[3] = 1
        print("TEAM PICK: ", AI.pick_team(state,team_sizes[current_quest]))
        state[12 + leader] = 0
        state[3] = 0
        input("CONTINUE")

    state[4] = 1
    state[12 + leader] = 1
    prop = [float(i) for i in input("Team Prop? (0 1): ").split(" ")]

    state[27:32] = np.array(prop)
    print("TEAM VOTE: ", AI.vote_team(state))
    state[4] = 0
    state[12 + leader] = 0
    state[27:32] = np.zeros(5)
    input("CONTINUE")

    votes = [int(i) for i in input("Team Votes? (0 1): ").split(" ")]
    if np.sum(votes) >= 3:
        state[32:37] = prop
        state[12 + leader] = 1
        state[37:42] = np.array(votes)
        AI.show_team(state)
        state[12 + leader] = 0
        state[37:42] = np.zeros(5)
        state[32:37] = np.zeros(5)
    else:
        state[12 + leader] = 1
        state[37:42] = np.array(votes)
        AI.show_team(state)
        state[12 + leader] = 0
        state[37:42] = np.zeros(5)
        leader += 1
        leader %= 5
        continue

    input("CONTINUE")

    if prop[0] == 1:
        state[5] = 1
        state[32:37] = prop
        print("QUEST VOTE: ", AI.vote_quest(state))
        state[5] = 0
        state[32:37] = np.zeros(5)
        input("CONTINUE")

    quests[current_quest] = int(input("QUEST RESULT (-1 1): "))
    fail_votes = int(input("NUM FAIL VOTES: "))
    success_votes = team_sizes[current_quest] - fail_votes
    team_matrix.append(prop)
    fail_votes_list.append(fail_votes)

    evil_probs = QuestAnalyzer.compute(np.array(team_matrix), np.array(fail_votes_list))

    state[32:37] = prop
    state[6] = quests[current_quest]
    state[12 + leader] = 1
    state[43] = success_votes
    state[44] = fail_votes
    AI.see_quest(state)
    state[6] = 0
    state[12 + leader] = 0
    state[43] = 0
    state[44] = 0
    state[32:37] = np.zeros(5)

    if input("GUESS MERLIN (y)") == "y":
        print("MERLIN GUESS: ", AI.guess_merlin(state))

    current_quest += 1
    leader += 1
    leader %= 5
    input("CONTINUE END OF ROUND")
    print("\n" * 3)
