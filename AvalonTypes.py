from enum import IntEnum
import numpy as np

class Side(IntEnum):
    GOOD = 0
    EVIL = 1


class VisibleSide(IntEnum):
    GOOD = 0
    EVIL = 1
    UNKNOWN = 2


class Role(IntEnum):
    GOOD = 0
    EVIL = 1
    MERLIN = 2

    @classmethod
    def get_name(cls, value):
        return cls(value).name

    @classmethod
    def is_good(cls, role):
        return role == cls.GOOD or role == cls.MERLIN

    @classmethod
    def is_evil(cls, role):
        return role == cls.EVIL


class VisibleRole(IntEnum):
    GOOD = 0
    EVIL = 1
    MERLIN = 2
    UNKNOWN = 3


class Phase(IntEnum):
    TEAM_BUILD = 0
    QUEST = 1
    # TEAM_PROP = 0
    # TEAM_VOTE = 1
    # QUEST_VOTE = 2

    @staticmethod
    def next(value):
        return (value + 1) % len(Phase)


class TeamVote(IntEnum):
    APPROVE = 0
    REJECT = 1


class QuestVote(IntEnum):
    SUCCESS = 0
    FAIL = 1


class QuestResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1
    UNDEF = 2

class QuestAnalyzer:
    """
    team_matrix - 2d array, [num_quests,num_players] one-hot of quest teams
    fail_votes - 1d array of the number of fail votes for each quest
    N - number of players in game
    """
    def compute(team_matrix,fail_votes):
        assert(len(team_matrix) == len(fail_votes))
        N = len(team_matrix[0])
        evil_counts = np.zeros(N)
        num_possible_states = 0
        #loop over all possible ways evil could be places
        for i in range(0,N):
            for j in range(i+1,N):
                #check if possible
                possible = True
                for t in range(len(team_matrix)):
                    c = team_matrix[t,i] + team_matrix[t,j]
                    if fail_votes[t] > c:
                        possible = False
                        break
                if possible:
                    num_possible_states += 1
                    evil_counts[i] += 1
                    evil_counts[j] += 1
        return evil_counts / num_possible_states
