import numpy as np

from Player import *

# http://upload.snakesandlattes.com/rules/r/ResistanceAvalon.pdf


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

    team size           (1)                2-4
    quest succeed votes (1)                2-4
    quest fail votes    (1)                2-4
    """

    def __init__(self, players):
        assert len(players) == 5

        self.N = 5
        self.players = players
        self.roles = np.array([-1, -1, 1, 1, 2])

        np.random.shuffle(self.roles)
        self.sides = (self.roles > 0) * 2 - 1
        self.leader = np.random.randint(self.N)
        self.quests = np.zeros(self.N)

        self.team = np.zeros(self.N)
        self.team_vote = np.zeros(self.N)

        self.team_r = 0
        self.quest_r = 0

        self.team_size = 2
        self.quest_succeed_votes = 0
        self.quest_fail_votes = 0

        self.state_size = 45
        pass

    def increment_leader(self):
        self.leader += 1
        self.leader %= self.N

    def set_team_size(self, team_size):
        self.team_size = team_size

    def get_visible_roles(self, role, i):
        assert role in [-1, 1, 2]
        if role == -1:
            return self.roles * (self.roles == -1)
        if role == 1:
            mask = np.zeros(self.N)
            mask[i] = 1
            return self.roles * mask
        if role == 2:
            return self.roles

    def get_visible_sides(self, role, i):
        assert role in [-1, 1, 2]
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

    def get_state(self, i):

        state = np.zeros(self.state_size)

        state[0] = self.sides[i]
        state[1] = self.roles[i]

        state[2] = 1 if i == self.leader else 0

        state[3] = 1  # need team proposition
        state[4] = 1  # need team vote
        state[5] = 1  # need quest vote
        state[6] = self.quest_r

        state[7:12] = self.get_visible_sides(state[1], i)
        state[12:17] = self.get_visible_roles(state[1], i)
        state[17:22] = self.get_visible_leader()

        state[22:27] = self.quests

        state[27:32] = self.team  # proposed team
        state[32:37] = self.team  # selected team
        state[37:42] = self.team_vote  # who voted how

        state[42] = self.team_size
        state[43] = self.quest_succeed_votes
        state[44] = self.quest_fail_votes

        return state

    def mask_state(self, state, mode="all"):
        mask = np.zeros(self.state_size)
        mask[0] = 1  # always show own side
        mask[1] = 1  # always show own role
        mask[2] = 1  # always show leader
        mask[22:27] = 1  # always show current quests
        mask[42] = 1  # always show team size

        if mode == "all":
            mask[:] = 1
        if mode == "start":
            mask[7:22] = 1  # show visible sides, roles, leaders
        if mode == "team_prop":
            mask[3] = 1  # nead team prop
            mask[17:22] = 1  # show leaders
        if mode == "team_vote":
            mask[4] = 1  # need team vote
            mask[17:22] = 1  # show leaders
            mask[27:32] = 1  # show proposition
        if mode == "team_fail_info":
            mask[17:22] = 1  # show leaders
            mask[37:42] = 1  # show votes
        if mode == "team_pass_info":
            mask[17:22] = 1  # show leaders
            mask[32:37] = 1  # show team
            mask[37:42] = 1  # show votes
        if mode == "quest_vote":
            mask[5] = 1  # need quest vote
            mask[32:37] = 1  # show team
        if mode == "quest_info":
            mask[6] = 1  # quest result
            mask[17:22] = 1  # show leaders
            mask[32:37] = 1  # show team
            mask[43] = 1  # show quest succeed votes
            mask[44] = 1  # show quest fail votes
        if mode == "none":
            pass
        return state * mask

    def start_game(self):
        # give first input to each agent
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, "start")
            player.see_start(state)

    def get_team(self):
        # have leader select team
        player = self.players[self.leader]
        state = self.get_state(self.leader)
        state = self.mask_state(state, "team_prop")
        self.team = player.pick_team(state)
        indices = self.team.argsort()[-self.team_size :]
        self.team = np.zeros(self.N)
        self.team[indices] = 1

    def vote_team(self):
        # everyone sees proposed team and votes
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, "team_vote")
            self.team_vote[i] = player.vote_team(state)

        self.team_r = self.team_vote.sum() >= self.N / 2

    def show_team(self):
        # everyone sees selected team and who picked it
        team_mask = "team_pass_info" if self.team_r else "team_fail_info"
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, team_mask)
            player.show_team(state)

    def vote_quest(self):
        # members of quest vote
        quest_votes = []
        self.quest_succeed_votes = 0
        self.quest_fail_votes = 0
        for i, player in enumerate(self.players):
            if int(self.team_vote[i]) == 0:
                continue
            state = self.get_state(i)
            state = self.mask_state(state, "quest_vote")
            if player.vote_quest(state):
                self.quest_succeed_votes += 1
            else:
                self.quest_fail_votes += 1

        assert self.quest_succeed_votes + self.quest_fail_votes == self.team_size
        self.quest_r = not self.quest_fail_votes

    def show_quest(self):
        # everyone sees quest result
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, "quest_info")
            player.see_quest(state)


class AvalonRunner:
    def __init__(self):
        players = [HumanPlayer() for i in range(5)]
        self.game = Avalon(players)
        self.quest = 0
        self.team_sizes = [2, 3, 2, 3, 3]

    def run_game(self):
        self.game.start_game()
        for team_size in self.team_sizes:
            self.game.set_team_size(team_size)
            self.game.get_team()
            self.game.vote_team()
            self.game.show_team()
            if self.game.team_r:  # extracting vote result
                self.game.vote_quest()
                self.game.show_quest()
            self.game.increment_leader()


runner = AvalonRunner()
runner.run_game()
