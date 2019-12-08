from enum import IntEnum


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
