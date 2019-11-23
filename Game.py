
#http://upload.snakesandlattes.com/rules/r/ResistanceAvalon.pdf
class Avalon:
    """
    Roles:  -1  0  1  2
             E  ?  G  M

    Sides:  -1  0  1
             E  ?  G

    Quest:  -1  0  1
             F  ?  P
    """

    def __init__(self, players):
        #5 player version
        # M G G E E
        assert(len(players) = 5)
        self.roles = np.random.shuffle(np.array([-1,-1,1,1,2]))
        self.leader = np.random.randint(5)
        self.quests = np.zeros()
        pass

    def start_game(self):
        #give first input to each agent
        #first input is just info about player roles
        #all zeros unless own role is merlin
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
