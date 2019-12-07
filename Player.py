import numpy as np
import tensorflow as tf

class Player:

    def __init__(self):
        pass

    def see_start(self, state):
        #show player start state
        #no return
        pass

    def pick_team(self, state):
        #show player state
        #request for team to be selected
        pass

    def vote_team(self, state):
        #inform player of proposed team
        #request for team vote
        pass

    def show_team(self, state):
        #inform player of selected team (or if no team picked)
        #show player who votes
        #no return
        pass

    def vote_quest(self, state):
        #show who is on team
        #request for quest vote
        pass

    def see_quest(self, state):
        #show quest result
        #no return
        pass

    def guess_merlin(self, state):
        #request guess for merlin
        pass


class HumanPlayer(Player):

    def __init__(self):
        pass

    def reset(self):
        pass

    def role_to_name(self, role):
        if role == -1:
            return 'EVIL'
        if role == 0:
            return '????'
        if role == 1:
            return 'GOOD'
        if role == 2:
            return 'MERL'

    def see_start(self,state):
        print(self.role_to_name(state[1]))
        if state[2]:
            print("You are the leader")
        print([self.role_to_name(r) for r in state[12:17]])
        print()


    def pick_team(self,state):
        print("Pick a team: ")
        team = input("Team list: ")
        print()
        team_list = team.split(' ')
        return np.array(team_list)

    def vote_team(self,state):
        print("Proposed Team: ", state[27:32])
        print("Leader: ", state[17:22])
        vote = input("Vote for Team (0,1): ")
        print()
        return int(vote)

    def show_team(self,state):
        print("Votes Team: ", state[37:42])
        print("Selected Team: ", state[32:37])
        print("Leader: ", state[17:22])
        print()

    def vote_quest(self,state):
        print("Selected Team: ", state[32:37])
        vote = input("Do Quest (0,1): ")
        print()
        return int(vote)

    def see_quest(self,state):
        print("Selected Team: ", state[32:37])
        print("Quest Result: ", state[6], "Fail Votes: ", state[44])
        print("Quests: ", state[22:27])

    def guess_merlin(self, state):
        team = input("Guess Merlin: ")
        print()
        team_list = team.split(' ')
        return np.array(team_list)
