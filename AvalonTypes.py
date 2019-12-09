from enum import IntEnum


class Side(IntEnum):
    GOOD = 0
    EVIL = 1


class VisibleSide(IntEnum):
    GOOD = 0
    EVIL = 1
    UNKNOWN = 2

assert Side.GOOD == VisibleSide.GOOD
assert Side.EVIL == VisibleSide.EVIL

class Role(IntEnum):
    GOOD = 0
    EVIL = 1
    MERLIN = 2

    @staticmethod
    def to_side(role):
        if role == Role.MERLIN:
            return Side.GOOD
        else:
            return role

    @staticmethod
    def to_visible_side(viewer, role, is_self):
        if is_self:
            return Role.to_side(viewer)
        if viewer == Role.GOOD:
            return VisibleSide.UNKNOWN
        if viewer == Role.EVIL:
            if role == Role.EVIL:
                return role
            else:
                return VisibleSide.UNKNOWN
        if viewer == Role.MERLIN:
            return role

    @staticmethod
    def to_visible_role(viewer, role, is_self):
        if is_self:
            return viewer
        if viewer == Role.GOOD:
            return VisibleRole.UNKNOWN
        if viewer == Role.EVIL:
            if role == Role.EVIL:
                return role
            else:
                return VisibleRole.UNKNOWN
        if viewer == Role.MERLIN:
            return role

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

assert Role.GOOD == Side.GOOD
assert Role.EVIL == Side.EVIL

assert Role.GOOD == VisibleRole.GOOD
assert Role.EVIL == VisibleRole.EVIL
assert Role.MERLIN == VisibleRole.MERLIN

class Phase(IntEnum):
    START = 0
    TEAM_BUILD = 1
    QUEST = 2
    MERLIN_GUESS = 3

    @staticmethod
    def next(value):
        return (value + 1) % len(Phase)


class TeamVote(IntEnum):
    APPROVE = 0
    REJECT = 1


class TeamResult(IntEnum):
    APPROVE = 0
    REJECT = 1
    UNDEF = 2

assert TeamVote.APPROVE == TeamResult.APPROVE
assert TeamVote.REJECT == TeamResult.REJECT

class QuestVote(IntEnum):
    SUCCESS = 0
    FAIL = 1


class QuestResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1
    UNDEF = 2

assert QuestVote.SUCCESS == QuestResult.SUCCESS
assert QuestVote.FAIL == QuestResult.FAILURE

class GameResult(IntEnum):
    GOOD_WIN = 0
    EVIL_WIN = 1
    UNDEF = 2

assert GameResult.GOOD_WIN == Side.GOOD
assert GameResult.EVIL_WIN == Side.EVIL
