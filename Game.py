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

    Votes:  0  1
            N  Y


    State:
    contents            size            values
    ###########################################
    own side            (1)             -1   1
    own role            (1)             -1   1 2

    is leader           (1)                0 1

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

        self.state_size = 42
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

    def get_state(self, i, on_quest = 0, quest_r = 0):

        state = np.zeros(self.state_size)

        state[0] = self.sides[i]
        state[1] = self.roles[i]

        state[2] = 1 if i == self.leader else 0

        state[3] = 1 #need team proposition
        state[4] = 1 #need team vote
        state[5] = 1 #need quest vote
        state[6] = quest_r

        state[7:12] = self.get_visible_sides(state[1], i)
        state[12:17] = self.get_visible_roles(state[1], i)
        state[17:22] = self.get_visible_leader()

        state[22:27] = self.quests

        state[27:32] = self.team #proposed team
        state[32:37] = self.team #selected team
        state[37:42] = self.team_vote #who voted how

        return state

    def mask_state(self, state, mode = 'all'):
        mask = np.zeros(self.state_size)
        mask[0] = 1 #always show own side
        mask[1] = 1 #always show own role
        mask[2] = 1 #always show leader
        mask[22:27] = 1 #always show current quests

        if mode == 'all':
            mask[:] = 1
        if mode == 'start':
            mask[7:22] = 1 #show visible sides, roles, leaders
        if mode == 'team_prop':
            mask[3] = 1 #nead team prop
            mask[17:22] = 1 #show leaders
        if mode == 'team_vote':
            mask[4] = 1 #need team vote
            mask[17:22] = 1 #show leaders
            mask[27:32] = 1 #show proposition
        if mode == 'team_fail_info':
            mask[17:22] = 1 #show leaders
            mask[37:42] = 1 #show votes
        if mode == 'team_pass_info':
            mask[17:22] = 1 #show leaders
            mask[32:37] = 1 #show team
            mask[37:42] = 1 #show votes
        if mode == 'quest_vote':
            mask[5] = 1 #need quest vote
            mask[32:37] = 1 #show team
        if mode == 'quest_info':
            mask[6] = 1 #quest result
            mask[17:22] = 1 #show leaders
            mask[32:37] = 1 #show team
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
        self.team = player.pick_team(state)


    def vote_team(self):
        #everyone sees proposed team and votes
        for i,player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state,'team_vote')
            self.team_vote[i] = player.see_start(state)

        #TODO did vote pass

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
game.get_team()
game.vote_team()
