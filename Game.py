import numpy as np
import tensorflow as tf
from Player import *
from AvalonTypes import *

# http://upload.snakesandlattes.com/rules/r/ResistanceAvalon.pdf


class GameState:
    def __init__(self, fields, size):
        self.state = np.zeros(size)
        self.fields = fields

    def __len__(self):
        return len(self.state)

    def _get_field(self, key):
        if key in self.fields:
            return self.fields[key]
        else:
            raise KeyError(f"key '{key}' not found")

    def _get_slice(self, key):
        if key.start is not None and key.stop is not None:
            if key.step is None:
                return self.state[key]
            else:
                start, stop, step = key.start, key.stop, key.step
                return self.state[start:stop].reshape((-1, step)).argmax(axis=1)
        elif key == slice(None):
            return self.state
        else:
            raise KeyError("ill-formed slice")

    def _get_array_index(self, key, arr_key):
        key = self._get_field(key)
        start, stop, step = key.start, key.stop, key.step
        if isinstance(arr_key, (int, np.integer)):
            start += arr_key * step
            return np.argmax(self.state[start : start + step])
        elif isinstance(arr_key, slice):
            if arr_key == slice(None):
                return self.state[start:stop].reshape((-1, step)).argmax(axis=1)
            else:
                raise NotImplementedError("slicing the array")
        else:
            raise KeyError("array key must be an int or slice")

    def __getitem__(self, key):
        if isinstance(key, str):
            key = self._get_field(key)

        if isinstance(key, (int, np.integer)):  # number
            return self.state[key]
        elif isinstance(key, slice):  # field, set, or array slice
            return self._get_slice(key)
        elif isinstance(key, tuple):  # array index or slice
            return self._get_array_index(*key)
        else:
            raise KeyError("key must be a string, int, slice, tuple(string, int/slice)")

    def _set_slice(self, key, value):
        # field, set, or array slice
        if key.start is not None and key.stop is not None:
            if key.step is None:  # field or set slice
                if isinstance(value, (int, np.integer)):  # field
                    self.state[key] = 0
                    self.state[key.start + value] = 1
                elif hasattr(type(value), "__iter__"):  # set
                    self.state[key] = 0
                    start = key.start
                    for index in value:
                        self.state[start + index] = 1
                else:
                    raise ValueError("value must be an int or iterable")
            else:  # array slice
                raise NotImplementedError("setting array slice")
        # whole slice
        elif key == slice(None):
            if isinstance(value, np.ndarray):
                self.state = value
            else:
                raise ValueError("value was not a numpy array")
        else:
            raise KeyError("ill-formed slice")

    def _set_array_index(self, key, arr_key, value):
        key = self._get_field(key)
        start, stop, step = key.indices(key.stop)
        arr_idx = range(start, stop, step)
        if isinstance(arr_key, (int, np.integer)):
            arr_start = arr_idx[arr_key]
            self.state[arr_start : arr_start + step] = 0
            self.state[arr_start + value] = 1
        elif isinstance(arr_key, slice):
            for i, val in zip(arr_idx[arr_key], value):
                self.state[i : i + step] = 0
                self.state[i + val] = 1
        else:
            raise KeyError("array key must be an int or slice")

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = self._get_field(key)

        if isinstance(key, (int, np.integer)):  # number
            self.state[key] = value
        elif isinstance(key, slice):  # field, set, or array slice
            self._set_slice(key, value)
        elif isinstance(key, tuple):  # array index or slice
            self._set_array_index(*key, value)
        else:
            raise KeyError("key must be a string, int, slice, tuple(string, int/slice)")

    def __delitem__(self, key):
        if isinstance(key, str):
            key = self._get_field(key)

        if isinstance(key, (int, np.integer)):  # number
            self.state[key] = 0
        elif isinstance(key, slice):  # field, set, or array slice
            start, stop, _ = key.indices(key.stop)
            self.state[start : stop] = 0
        else:
            raise KeyError("key must be an int or slice")

    def get_field(self, key):
        return np.argmax(self.__getitem__(key))

    def get_elements(self, key):
        return np.nonzero(self.__getitem__(key))[0]

    def get_vector(self):
        return self.state


class GameStateBuilder:
    def __init__(self):
        self.fields = {}
        self.size = 0

    def add_number(self, field_name):
        assert field_name not in self.fields, f"'{field_name}' already a field"
        self.fields[field_name] = self.size
        self.size += 1
        return self

    def add_field(self, field_name, size):
        assert field_name not in self.fields, f"'{field_name}' already a field"
        assert size > 1
        self.fields[field_name] = slice(self.size, self.size + size)
        self.size += size
        return self

    def add_array(self, field_name, size, num_vals):
        assert field_name not in self.fields, f"'{field_name}' already a field"
        arr_size = size * num_vals
        self.fields[field_name] = slice(self.size, self.size + arr_size, num_vals)
        self.size += arr_size
        return self

    def build(self):
        return GameState(self.fields, self.size)


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

    @staticmethod
    def create_state(N):
        return (
            GameStateBuilder()
            # static knowledge
            .add_field("own_side", len(Side))
            .add_field("own_role", len(Role))
            .add_array("visible_sides", N, len(VisibleSide))
            .add_array("visible_roles", N, len(VisibleRole))
            # game round info
            .add_field("phase", len(Phase))
            .add_number("is_leader")
            .add_field("leader", N)
            .add_field("quest", N)
            .add_number("quest_num")
            .add_array("quest_results", N, len(QuestResult))
            .add_number("consec_rejects")
            .add_field("game_result", len(GameResult))
            # team building phase info
            .add_number("need_team_prop")
            .add_number("need_team_vote")
            .add_number("team_size")
            .add_field("team_prop", N)
            .add_field("team_votes", N)
            .add_field("team_result", len(TeamResult))
            # quest phase info
            .add_number("need_quest_vote")
            .add_number("quest_size")
            .add_field("quest_team", N)
            .add_number("quest_success_votes")
            .add_number("quest_fail_votes")
            .add_field("quest_result", len(QuestResult))
            .build()
        )

    def __init__(self, players):
        assert len(players) == 5

        self.N = 5
        self.team_sizes = [2, 3, 2, 3, 3]
        self.players = players
        self.states = [Avalon.create_state(self.N) for player in players]
        self.roles = np.array(2 * [Role.GOOD] + 2 * [Role.EVIL] + [Role.MERLIN])

    def _show_roles(self):
        for i, (player, state, role) in enumerate(self.players, self.states, self.roles):
            state["own_side"] = Role.to_side(role)
            state["own_role"] = role
            state["visible_sides", :] = self.get_visible_sides(role, i)
            state["visible_roles", :] = self.get_visible_roles(role, i)

    def _start_round(self):
        for i, state in enumerate(self.states):
            state["phase"] = self.phase
            state["is_leader"] = i == self.leader
            state["leader"] = self.leader
            state["quest"] = self.current_quest
            state["quest_num"] = self.current_quest
            state["quest_results", :] = self.quests
            state["consec_rejects"] = self.proposed_team_counter

    def reset(self):
        np.random.shuffle(self.roles)
        self.sides = np.array([Role.to_side(role) for role in self.roles])
        self.leader = np.random.randint(self.N)
        self.current_quest = 0
        self.quests = np.full(self.N, QuestResult.UNDEF)
        self.proposed_team_counter = 0
        self.phase = Phase.START

        self.team = np.zeros(self.N)
        self.team_size = self.team_sizes[self.current_quest]
        self.team_vote = np.zeros(self.N)

        self.quest_succeed_votes = 0
        self.quest_fail_votes = 0

        self.team_r = TeamResult.UNDEF
        self.quest_r = QuestResult.UNDEF
        self.game_result = GameResult.UNDEF
        self.merlin_discovered = False

        self._show_roles()
        # return self.set_state()

    def increment_leader(self):
        self.leader += 1
        self.leader %= self.N

    def get_visible_roles(self, role, i):
        assert role in [Role.GOOD, Role.EVIL, Role.MERLIN]
        return np.array([Role.to_visible_role(role, r, i == j) for j, r in enumerate(self.roles)])

    def get_visible_sides(self, role, i):
        assert role in [Role.GOOD, Role.EVIL, Role.MERLIN]
        return np.array([Role.to_visible_side(role, r, i == j) for j, r in enumerate(self.roles)])

#     def get_visible_leader(self):
#         leaders = np.zeros(self.N)
#         leaders[self.leader] = 1
#         return leaders

    def set_state(self, i, phase, prop_team=False, vote_team=False, vote_quest=False):
        state = self.states[i]

        # game round info
        state["phase"] = self.phase
        state["is_leader"] = i == self.leader
        state["leader"] = self.leader
        state["quest"] = self.current_quest
        state["quest_num"] = self.current_quest
        state["quest_results", :] = self.quests
        state["consec_rejects"] = self.proposed_team_counter

        if phase == Phase.START:
            return state

        # team_building phase info
        if phase == Phase.TEAM_BUILD:
            state["need_team_prop"] = prop_team
            state["need_team_vote"] = vote_team
            state["team_size"] = self.team_size
            # TODO: fix these
            state["team_prop"] = np.nonzero(self.team)[0]
            state["team_votes"] = np.nonzero(self.team_vote)[0]
            #####
            state["team_result"] = self.team_r
        else:
            del state["need_team_prop"]
            del state["need_team_vote"]
            del state["team_size"]
            del state["team_prop"]
            del state["team_votes"]
            del state["team_result"]

        # quest phase info
        if phase == Phase.QUEST:
            state["need_quest_vote"] = vote_quest
            state["quest_team"] = np.nonzero(self.team[0]) # TODO: fix
            state["quest_success_votes"] = self.quest_succeed_votes
            state["quest_fail_votes"] = self.quest_fail_votes
            state["quest_result"] = self.quest_r # TODO is quest_r reset?
        else:
            del state["need_quest_vote"]
            del state["quest_team"]
            del state["quest_success_votes"]
            del state["quest_fail_votes"]
            del state["quest_result"]

        return state

    # def mask_state(self, state, mode="all"):
    #     mask = np.zeros(self.state_size)
    #     mask[0] = 1  # always show own side
    #     mask[1] = 1  # always show own role
    #     mask[2] = 1  # always show leader
    #     mask[7:22] = 1  # always show visible sides, roles, leaders
    #     mask[22:27] = 1  # always show current quests
    #     mask[42] = 1  # always show team size

    #     if mode == "all":
    #         mask[:] = 1
    #     if mode == "start":
    #         pass
    #     if mode == "team_prop":
    #         mask[3] = 1  # nead team prop
    #         mask[17:22] = 1  # show leaders
    #     if mode == "team_vote":
    #         mask[4] = 1  # need team vote
    #         mask[17:22] = 1  # show leaders
    #         mask[27:32] = 1  # show proposition
    #     if mode == "team_fail_info":
    #         mask[17:22] = 1  # show leaders
    #         mask[37:42] = 1  # show votes
    #     if mode == "team_pass_info":
    #         mask[17:22] = 1  # show leaders
    #         mask[32:37] = 1  # show team
    #         mask[37:42] = 1  # show votes
    #     if mode == "quest_vote":
    #         mask[5] = 1  # need quest vote
    #         mask[32:37] = 1  # show team
    #     if mode == "quest_info":
    #         mask[6] = 1  # quest result
    #         mask[17:22] = 1  # show leaders
    #         mask[32:37] = 1  # show team
    #         mask[43] = 1  # show quest succeed votes
    #         mask[44] = 1  # show quest fail votes
    #     if mode == "none":
    #         pass
    #     return state * mask

    def start_game(self):
        # give first input to each agent
        for i, player in enumerate(self.players):
            state, side, role = self.states[i], self.sides[i], self.roles[i]
            print(side)
            state["own_side"] = side
            state["own_role"] = role
            state["visible_sides", :] = self.get_visible_sides(role, i)
            state["visible_roles", :] = self.get_visible_roles(role, i)

            # state = self.get_state(i)
            # state = self.mask_state(state, "start")
            self.set_state(i, Phase.START, start=True)
            player.see_start(state.get_vector())

    # returns a list of the indices of players to put on the team
    def get_team(self):
        # have leader select team
        self.team_size = self.team_sizes[self.current_quest]
        leader = self.players[self.leader]
        state = self.states[self.leader]

        # state = self.get_state(self.leader)
        # state = self.mask_state(state, "team_prop")
        self.set_state(self.leader, Phase.TEAM_BUILD, prop_team=True)
        team_probs = leader.pick_team(state.get_vector())
        # TODO .pick_team returns booleans, but treated as probabilities!

        on_team = self.team.argsort()[-self.team_size :]
        self.team = np.zeros(self.N)
        self.team[on_team] = 1

    def vote_team(self):
        # everyone sees proposed team and votes
        for i, player in enumerate(self.players):
            state = self.states[i]
            # state = self.get_state(i)
            # state = self.mask_state(state, "team_vote")
            self.set_state(i, Phase.TEAM_BUILD, vote_team=True)
            self.team_vote[i] = player.vote_team(state.get_vector())

        if self.team_vote.sum() >= self.N / 2:
            self.team_r = TeamResult.APPROVE
        else:
            self.team_r = TeamResult.REJECT

    def show_team(self):
        # everyone sees selected team and who picked it
        # team_mask = "team_pass_info" if self.team_r else "team_fail_info"
        for i, player in enumerate(self.players):
            state = self.states[i]
            # state = self.get_state(i)
            # state = self.mask_state(state, team_mask)
            self.set_state(i, Phase.TEAM_BUILD, show_team=True)
            player.show_team(state.get_vector())

        if self.team_r == TeamResult.REJECT:
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
            state = self.states[i]
            # state = self.get_state(i)
            # state = self.mask_state(state, "quest_vote")
            self.set_state(i, Phase.QUEST, vote_quest=True)
            if np.array(player.vote_quest(state.get_vector())) == 1 or self.sides[i] == Side.GOOD:
                self.quest_succeed_votes += 1
            else:
                self.quest_fail_votes += 1

        assert self.quest_succeed_votes + self.quest_fail_votes == self.team_size
        if self.quest_fail_votes:
            self.quest_r = QuestResult.FAILURE
        else:
            self.quest_r = QuestResult.SUCCESS
        self.quests[self.current_quest] = self.quest_r

    def show_quest(self):
        # everyone sees quest result
        for i, player in enumerate(self.players):
            state = self.states[i]
            # state = self.get_state(i)
            # state = self.mask_state(state, "quest_info")
            self.set_state(i, Phase.QUEST, show_quest=True)
            player.see_quest(state.get_vector())

        # end of round, so increment leader and current quest
        self.increment_leader()
        self.current_quest += 1

    def guess_merlin(self):
        guesses = np.zeros(self.N)
        for i, player in enumerate(self.players):
            if self.sides[i] != Side.EVIL:
                continue
            state = state[i]
            # state = self.get_state(i)
            # state = self.mask_state(state, "none")
            self.set_state(i, Phase.MERLIN_GUESS)
            guesses += player.guess_merlin(state.get_vector())

        self.merlin_discovered = self.roles[np.argmax(guesses)] == Role.MERLIN
        if self.merlin_discovered:
            self.game_result = GameResult.EVIL_WIN

    def is_over(self):
        # too many proposed teams failed so evil wins
        if self.proposed_team_counter >= 5:
            self.game_result = GameResult.EVIL_WIN
            return self.game_result

        maj = np.ceil(self.N / 2)
        if np.sum(self.quests == QuestResult.SUCCESS) >= maj:
            self.game_result = GameResult.GOOD_WIN
        if np.sum(self.quests == QuestResult.FAILURE) >= maj:
            self.game_result = GameResult.EVIL_WIN
        return self.game_result

    def winning_side(self):
        return self.game_result

    def get_game_result(self):
        return self.sides == self.game_result


class AvalonRunner:
    def __init__(self):
        players = [HumanPlayer() for i in range(5)]
        self.game = Avalon(players)

    def run_game(self):
        self.game.reset()
        self.game.start_game()
        while self.game.is_over() == GameResult.UNDEF:
            self.game.get_team()
            self.game.vote_team()
            self.game.show_team()
            if self.game.team_r == TeamResult.APPROVE:  # extracting vote result
                self.game.vote_quest()
                self.game.show_quest()

        if self.game.winning_side() == GameResult.GOOD_WIN:
            self.game.guess_merlin()

        return self.game.get_game_result()


if __name__ == "__main__":
    runner = AvalonRunner()
    print(runner.run_game())
