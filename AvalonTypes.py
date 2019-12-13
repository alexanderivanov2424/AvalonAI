import numpy as np

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
