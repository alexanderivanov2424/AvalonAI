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
    is on quest         (1)                0 1

    need team prop      (1)                0 1
    need team vote      (1)                0 1
    need quest vote     (1)                0 1
    quest result        (1)                0 1

    visible sides       (5)             -1 0 1
    visible roles       (5)             -1 0 1 2
    who is leader       (5)                0 1

    current quests      (5)             -1 0 1

    team proposition    (5)                0 1
    team selected       (5)                0 1
    team votes          (5)                0 1
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

        self.team = np.zeros(self.N)
        self.team_vote = np.zeros(self.N)

        self.state_size = 43
        pass

    def get_visible_roles(self,role, i):
        assert(role in [-1,1,2])
        if role == -1:
            return self.roles * (self.roles == -1)
        if role == 1:
            mask = np.zeros(self.N)
            mask[i] = 1
            return self.roles * mask
        if role == 2:
            return self.roles

    def get_visible_sides(self,role, i):
        assert(role in [-1,1,2])
        if role == -1:
            return self.sides
        if role == 1:
            mask = np.zeros(self.N)
            mask[i] = 1
            return self.sides * mask
        if role == 2:
            return self.sides

    def get_visible_leader(self):
        leaders = np.zeros(self.N)
        leaders[self.leader] = 1
        return leaders

    def get_state(self, i, on_quest = 0, quest_r = 0, team_p = None, team_s = None, team_v = None):
        if team_p == None:
            team_p = np.zeros(self.N)
        if team_s == None:
            team_s = np.zeros(self.N)
        if team_v == None:
            team_v = np.zeros(self.N)

        state = np.zeros(self.state_size)

        state[0] = self.sides[i]
        state[1] = self.roles[i]

        state[2] = 1 if i == self.leader else 0
        state[3] = on_quest

        state[4] = 1 #need team proposition
        state[5] = 1 #need team vote
        state[6] = 1 #need quest vote
        state[7] = quest_r

        state[8:13] = self.get_visible_sides(state[1], i)
        state[13:18] = self.get_visible_roles(state[1], i)
        state[18:23] = self.get_visible_leader()

        state[23:28] = self.quests

        state[28:33] = team_p #proposed team
        state[33:38] = team_s #selected team
        state[38:43] = team_v #who voted how

        return state

    def mask_state(self, state, mode = 'all'):
        mask = np.zeros(self.state_size)
        mask[0] = 1 #always show own side
        mask[1] = 1 #always show own role
        mask[2] = 1 #always show leader
        mask[23:28] = 1 #always show current quests

        if mode == 'all':
            mask[:] = 1
        if mode == 'start':
            mask[8:23] = 1 #show visible sides, roles, leaders
        if mode == 'team_prop':
            mask[4] = 1 #nead team prop
            mask[18:23] = 1 #show leaders
        if mode == 'team_vote':
            mask[3] = 1 #need team vote
            mask[18:23] = 1 #show leaders
            mask[23:28] = 1 #show proposition
        if mode == 'team_fail_info':
            mask[18:23] = 1 #show leaders
            mask[38:43] = 1 #show votes
        if mode == 'team_pass_info':
            mask[18:23] = 1 #show leaders
            mask[23:28] = 1 #show team
            mask[38:43] = 1 #show votes
        if mode == 'quest_vote':
            mask[6] = 1 #need quest vote
            mask[23:28] = 1 #show team
        if mode == 'quest_info':
            mask[7] = 1 #quest result
            mask[18:23] = 1 #show leaders
            mask[23:28] = 1 #show team
        if mode == 'none':
            pass
        return state * mask

    def start_game(self):
        #give first input to each agent
        for i,player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state,'start')
            player.see_start(state)

    def get_team(self):
        #have leader select team
        player = self.players[self.leader]
        state = self.get_state(self.leader)
        state = self.mask_state(state,'team_prop')
        team = player.pick_team(state)


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
