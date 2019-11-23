import numpy as np

from Player import Player


#http://upload.snakesandlattes.com/rules/r/ResistanceAvalon.pdf
class Avalon:
    """
    5 player version
    M G G E E


    Roles:  -1  0  1  2
             E  ?  G  M

    Sides:  -1  0  1
             E  ?  G

    Quest:  -1  0  1
             F  ?  P


    State:
    contents            size            values
    ###########################################
    own side            (1)             -1   1
    own role            (1)             -1   1 2
    is leader           (1)                0 1

    need team vote      (1)                0 1
    need quest vote     (1)                0 1
    quest result        (1)                0 1

    visible sides       (5)             -1 0 1
    visible roles       (5)             -1 0 1 2
    who is leader       (5)                0 1

    current quests      (5)             -1 0 1

    team proposition    (5)                0 1
    team selected       (5)                0 1
    """

    def __init__(self, players):
        assert(len(players) == 5)

        self.N = 5
        self.players = players
        self.roles = np.array([-1,-1,1,1,2])

        np.random.shuffle(self.roles)
        self.sides = (self.roles > 0) * 2 - 1
        self.leader = np.random.randint(self.N)
        self.quests = np.zeros(self.N)
        pass

    def get_visible_roles(self,role):
        assert(role in [-1,1,2])
        if role == -1:
            return self.roles * (self.roles == -1)
        if role == 1:
            return self.roles * 0
        if role = 2:
            return self.roles

    def get_visible_sides(self,role):
        assert(role in [-1,1,2])
        if role in [-1,2]:
            return self.sides
        if role == 1:
            return self.sides * 0

    def get_visible_leader(self):
        leaders = np.zeros(self.N)
        leaders[self.leader] = 1
        return leaders

    def get_state(self, i, quest_r, team_p = np.zeros(self.N), team_s = np.zeros(self.N)):
        state = np.zeros(36)
        state[0] = self.sides[i]
        state[1] = self.roles[i]
        state[2] = 1 if i == self.leader else 0

        state[3] = 1
        state[4] = 1
        state[5] = quest_r

        state[6:11] = self.get_visible_sides(state[0])
        state[11:16] = self.get_visible_roles(state[1])
        state[16:21] = self.get_visible_leader()

        state[21:26] = self.quests

        state[26:31] = team_p
        state[31:36] = team_s
        return state

    def start_game(self):
        #give first input to each agent
        for i,player in enumerate(self.players):
            state = self.get_state(i,0)
            print(state)
        pass

    def get_team(self):
        #have leader select team
        pass

    def vote_team(self):
        #everyone sees proposed team and votes
        pass

    def show_team(self):
        #everyone sees selected team and who picked it
        pass

    def vote_quest(self):
        #members of quest vote
        pass

    def show_quest(self):
        #everyone sees quest result
        pass



#Testing
players = [Player() for i in range(5)]
game = Avalon(players)
game.start_game()
