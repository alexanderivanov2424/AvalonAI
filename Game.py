import numpy as np
import tensorflow as tf
from Player import *
from AvalonTypes import *


def rotate(L,i):
    return np.append(L[i:],L[:i])

class Avalon:

    def __init__(self, players):
        assert len(players) == 5

        self.N = 5
        self.team_sizes = [2, 3, 2, 3, 3]
        self.players = players
        self.roles = np.array([-1, -1, 1, 1, 2])

        np.random.shuffle(self.roles)
        self.sides = (self.roles > 0) * 2 - 1
        self.leader = np.random.randint(self.N)
        self.current_quest = 0
        self.quests = np.zeros(self.N)

        self.team_matrix = []
        self.fail_votes = []
        self.evil_probs = np.zeros(self.N)
        self.evil_probs = np.array([.4 for i in range(self.N)])

        self.team = np.zeros(self.N)
        self.team_vote = np.zeros(self.N)

        self.team_r = 0
        self.quest_r = 0

        self.team_size = 2
        self.quest_succeed_votes = 0
        self.quest_fail_votes = 0

        self.game_result = 0
        self.merlin_discovered = False
        self.state_size = 50

        self.proposed_team_counter = 0
        pass

    def increment_leader(self):
        self.leader += 1
        self.leader %= self.N

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

        state[7:12] = rotate(self.get_visible_sides(state[1], i),i)
        state[12:17] = rotate(self.get_visible_roles(state[1], i),i)
        state[17:22] = rotate(self.get_visible_leader(),i)

        state[22:27] = self.quests

        state[27:32] = rotate(self.team,i)  # proposed team
        state[32:37] = rotate(self.team,i)  # selected team
        state[37:42] = rotate(self.team_vote,i)  # who voted how

        state[42] = self.team_size
        state[43] = self.quest_succeed_votes
        state[44] = self.quest_fail_votes

        state[45:50] = rotate(self.evil_probs,i)

        return state

    def mask_state(self, state, mode="all"):
        mask = np.zeros(self.state_size)
        mask[0] = 1  # always show own side
        mask[1] = 1  # always show own role
        mask[2] = 1  # always show leader
        mask[7:22] = 1  # always show visible sides, roles, leaders
        mask[22:27] = 1  # always show current quests
        mask[42] = 1  # always show team size
        mask[45:50] = 1

        if mode == "all":
            mask[:] = 1
        if mode == "start":
            pass
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
        self.team_size = self.team_sizes[self.current_quest]
        leader = self.players[self.leader]
        state = self.get_state(self.leader)
        state = self.mask_state(state, "team_prop")
        self.team = rotate(leader.pick_team(state,self.team_size),-self.leader)
        on_team = self.team.argsort()[-self.team_size :]
        self.team = np.zeros(self.N)
        self.team[on_team] = 1

    def vote_team(self):
        # everyone sees proposed team and votes
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, "team_vote")
            self.team_vote[i] = player.vote_team(state) > .5

        self.team_r = self.team_vote.sum() >= self.N / 2

    def show_team(self):
        # everyone sees selected team and who picked it
        team_mask = "team_pass_info" if self.team_r else "team_fail_info"
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, team_mask)
            player.show_team(state)

        if self.team_r:
            self.proposed_team_counter = 0
        else:
            self.increment_leader()
            self.proposed_team_counter += 1

    def vote_quest(self):
        # members of quest vote
        quest_votes = []
        self.quest_succeed_votes = 0
        self.quest_fail_votes = 0
        for i, player in enumerate(self.players):
            if not self.team[i]:
                continue
            state = self.get_state(i)
            state = self.mask_state(state, "quest_vote")
            if np.array(player.vote_quest(state) > .5) == 1 or self.sides[i] == 1:
                self.quest_succeed_votes += 1
            else:
                self.quest_fail_votes += 1

        assert self.quest_succeed_votes + self.quest_fail_votes == self.team_size
        self.quest_r = not self.quest_fail_votes
        self.quests[self.current_quest] = 2 * self.quest_r - 1

        #prep for calculating probabilities
        self.fail_votes.append(self.quest_fail_votes)
        self.team_matrix.append(self.team)
        self.evil_probs = QuestAnalyzer.compute(np.array(self.team_matrix), np.array(self.fail_votes))

    def show_quest(self):
        # everyone sees quest result
        for i, player in enumerate(self.players):
            state = self.get_state(i)
            state = self.mask_state(state, "quest_info")
            player.see_quest(state)

        # end of round, so increment leader and current quest
        self.increment_leader()
        self.current_quest += 1

    def guess_merlin(self):
        guesses = np.zeros(self.N)
        for i, player in enumerate(self.players):
            if not self.roles[i] == -1:
                continue
            state = self.get_state(i)
            state = self.mask_state(state, "none")
            guesses += rotate(player.guess_merlin(state),-i)

        self.merlin_discovered = self.roles[np.argmax(guesses)] == 2
        if self.merlin_discovered:
            self.game_result = -1

    def is_over(self):
        # too many proposed teams failed so evil wins
        if self.proposed_team_counter >= 5:
            self.game_result = -1
            return self.game_result

        maj = np.ceil(self.N / 2)
        if np.sum(self.quests == -1) >= maj:
            self.game_result = -1
        if np.sum(self.quests == 1) >= maj:
            self.game_result = 1
        return self.game_result

    def winning_side(self):
        return self.game_result

    def get_game_result(self):
        return self.sides == self.game_result

"""
Tester Class with 5 human players
Runs by default when running Game.py
"""
class AvalonRunner:
    def __init__(self):
        players = [HumanPlayer() for i in range(5)]
        self.game = Avalon(players)

    def run_game(self):
        self.game.start_game()
        while not self.game.is_over():
            self.game.get_team()
            self.game.vote_team()
            self.game.show_team()
            if self.game.team_r:  # extracting vote result
                self.game.vote_quest()
                self.game.show_quest()

        if self.game.winning_side() == 1:
            self.game.guess_merlin()

        return self.game.get_game_result()


if __name__ == "__main__":
    runner = AvalonRunner()
    print(runner.run_game())
