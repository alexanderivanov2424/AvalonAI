

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
        print([self.role_to_name(r) for r in state[7:12]])


    def pick_team(self,state):
        print("Pick a team: ")
        team = input("Team list")
        team_list = eval(team)
        return np.array(team_list)

    def show_team(self, state):
        print()
