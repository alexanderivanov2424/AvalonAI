import numpy as np
import tensorflow as tf


class Player:
    def __init__(self):
        pass

    def see_start(self, state):
        # show player start state
        # no return
        pass

    def pick_team(self, state):
        # show player state
        # request for team to be selected
        pass

    def vote_team(self, state):
        # inform player of proposed team
        # request for team vote
        pass

    def show_team(self, state):
        # inform player of selected team (or if no team picked)
        # show player who votes
        # no return
        pass

    def vote_quest(self, state):
        # show who is on team
        # request for quest vote
        pass

    def see_quest(self, state):
        # show quest result
        # no return
        pass

    def guess_merlin(self, state):
        # request guess for merlin
        pass


class HumanPlayer(Player):
    def __init__(self):
        self.role_names = ""
        self.quest_info = []
        pass

    def role_to_name(self, role):
        if role == -1:
            return "EVIL"
        if role == 0:
            return "????"
        if role == 1:
            return "GOOD"
        if role == 2:
            return "MERL"

    def is_yes_no(self, s):
        s = s.lower()
        return s == "y" or s == "n"

    def get_yes_no(self, prompt):
        while True:
            vote = input(prompt + " (y/n): ")
            if self.is_yes_no(vote):
                return vote == "y"

    def get_team(self, team_size):
        ys = team_size
        ns = 5 - team_size
        while True:
            team = input(f"Pick a Team ({ys} y's, {ns} n's): ")
            team_list = team.split(" ")
            if len(team_list) != 5:
                continue
            if not all(self.is_yes_no(choice) for choice in team_list):
                continue
            team_list = [choice == "y" for choice in team_list]
            if len(np.nonzero(team_list)[0]) != team_size:
                continue
            return team_list

    def see_start(self, state):
        print("Your Role: ", self.role_to_name(state[1]))
        print("Roles You See: ", [self.role_to_name(r) for r in state[12:17]])
        print()

    def pick_team(self, state):
        team_size = int(state[42])
        print("You are the leader")
        team_list = self.get_team(team_size)
        print()
        return np.array(team_list)

    def vote_team(self, state):
        print("Proposed Team: ", ["X" if chosen else "_" for chosen in state[27:32]])
        print("Leader: ", np.argmax(state[17:22]))
        vote = self.get_yes_no("Accept Team?")
        print()
        return vote

    def show_team(self, state):
        print("Votes for Team: ", ["y" if vote else "n" for vote in state[37:42]])
        print("Selected Team: ", ["X" if going else "_" for going in state[32:37]])
        print("Leader: ", np.argmax(state[17:22]))
        print()

    def vote_quest(self, state):
        print("Selected Team: ", ["X" if going else "_" for going in state[32:37]])
        vote = self.get_yes_no("Succeed Quest?")
        print()
        return vote

    def see_quest(self, state):
        print("Selected Team: ", ["X" if going else "_" for going in state[32:37]])
        print(
            "Quest Result: ",
            "SUCCESS" if state[6] == 1 else "FAILURE",
            "Fail Votes: ",
            int(state[44]),
        )
        res_str = lambda res: "✔" if res == 1 else "✘" if res == -1 else "_"
        print("Quests: ", [res_str(result) for result in state[22:27]])

    def guess_merlin(self, state):
        team = input("Guess Merlin: ")
        print()
        team_list = team.split(" ")
        return np.array(team_list)
