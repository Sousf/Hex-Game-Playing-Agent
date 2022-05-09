from cmath import inf
import copy
from math import ceil, floor
from random import randint
import time
from numpy import average, log, sqrt, zeros, array, roll, vectorize
# from sqlalchemy import null



# borrowed from referee
_ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])
_HEX_STEPS = array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
    dtype="i,i")
_CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
    for n1, n2 in 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1))) + 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 2)))]


class Player:
    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue.
        """
        # put your code here
        self.n = n
        self.colour = player
        if self.colour == "red":
            self.opp_colour = "blue"
        else:
            self.opp_colour = "red"
        
        rows, cols = (self.n, self.n)
        self.internal_board = [[0 for i in range(cols)] for j in range(rows)]
        self.is_first_turn = True
        self.is_blues_first_turn = False
        self.cutoff_depth = 1
        self.radius = ceil((self.n-1)/2) - 1

        self.player_pieces_num = 0
        self.opp_pieces_num = 0
        self.player_sum = 0
        self.opp_sum = 0
        # self.last_action = null


    def _get_cutoff_depth(self, player_num, opp_num):
        # occupied = player_num + opp_num
        occupied = self.player_pieces_num + self.opp_pieces_num
        empty = (self.n)**2 - occupied

        if (empty <= 10):
            cutoff_depth = 4
        elif (empty > 10 and empty <= 30):
            cutoff_depth = 3
        elif (empty > 30 and empty <= 60):
            cutoff_depth = 2
        elif (empty >= 60):
            cutoff_depth = 1
        ###########
        # if (occupied == 0):
        #     cutoff_depth = 1
        # else:
        #     cutoff_depth = floor(1 + log(occupied/sqrt(self.n)))
        return (cutoff_depth)




    def _get_eval_score(self, s, a, colour):

        # Forming a chain get a positive score

        # find shortest path between start and last_coord

        # find the shortest path between last_coord and goal

        if(s[2] == 0):
            p_avg = 0
        else:
            p_avg = s[4]/s[2]
        if(s[3] == 0):
            opp_avg = 0
        else:
            opp_avg = s[5]/s[3]

        dist_from_diag_diff = -(p_avg - opp_avg)

        winning_reward = 0
        if (self._is_terminal(s, colour)):
            winning_reward = 100

        losing_penalty = 0
        if (colour == "red"):
            if (self._is_terminal(s, "blue")):
                losing_penalty = -200
        else:
            if (self._is_terminal(s, "red")):
                losing_penalty = -200
            

        eval_score = 0.5*(s[2] - s[3]) + 0.2*(dist_from_diag_diff) + winning_reward + losing_penalty

        return eval_score

    def _get_actions(self, s, colour):
        """
        Get all possible actions at the current state
        """
        # action = ("PLACE", r, q)
        actions = []
        for i in range(self.n):
            for j in range(self.n):
                if (s[0][i][j] == 0):
                    actions.append(("PLACE", i, j))
        if (self.is_blues_first_turn and colour == "blue"):
            actions.append(("STEAL", ))

        if (self.is_first_turn and colour == "red" and (("PLACE", (self.n-1)/2, (self.n-1)/2) in actions)):
            actions.remove(("PLACE", (self.n-1)/2, (self.n-1)/2))
        return actions

    def result(self, s, a, colour):
        """
        s: is the current internal board state
        a: the action we want to apply to the state
        return updated state with action a.
        """
        new_state = copy.deepcopy(s[0])

        # set defaults
        num_captured = 0
        stolen_dist = 0
    
        sum_dist_from_center = 0

        if (a[0] == "PLACE"):
            new_state[a[1]][a[2]] = colour
            num_captured, sum_dist_from_center = self.apply_capture(new_state, colour, (a[1], a[2]))
        elif (a[0] == "STEAL"):
            is_stealCoord_reached = False
            steal_coord = tuple()
            for i in range(self.n):
                if is_stealCoord_reached:
                    break
                for j in range(self.n):
                    if new_state != 0:
                        new_state[i][j] = 0
                        steal_coord = (i,j)
                        is_stealCoord_reached = True
                        break
            new_state[steal_coord[1]][steal_coord[0]] = "blue"
            stolen_dist = abs(self.n - 1 - steal_coord[0] - steal_coord[1])

        return [new_state, s[1], s[2], s[3], s[4], s[5]], num_captured, sum_dist_from_center, stolen_dist

    def _max_value(self, s, a, alpha, beta):
        """
        Player's turn
        Get the maximum of the minimum values
        """
        # s = [self.internal_board, depth, player_num, opp_num, p_sum, opp_sum]
        # s[1] += 1
        # print("max", s[1])
        # print("MAX: ############################")
        if (s[1] >= self.cutoff_depth or (self._is_terminal(s, self.colour))):
            return self._get_eval_score(s, a, self.colour)

        max_eval = -inf
        actions = self._get_actions(s, self.colour)
        # print("ACTIONS: ", actions)
        for a in actions:
            new, num_cap, captured_dist, stolen_dist = self.result(s, a, self.colour)
            dist_from_a = 0
            if a[0] == "PLACE":
                dist_from_a = abs(self.n - 1 - a[1] - a[2])
                stolen = 0
            else:
                stolen = 1

            if (self.colour == "blue"):
                v = self._min_value([new[0], new[1]+1, new[2]+1+stolen, new[3]-num_cap-stolen, new[4] + dist_from_a + stolen_dist,  new[5] - captured_dist - stolen_dist], a, alpha, beta)
            else:
                v = self._min_value([new[0], new[1]+1, new[2]+1, new[3]-num_cap, new[4] + dist_from_a - stolen_dist,  new[5] - captured_dist + stolen_dist], a, alpha, beta)

            # print("curr board num: ", (s[2], s[3]))
            # print("in the future placing: ", a)
            max_eval = max(v, max_eval)
            alpha = max(alpha, max_eval)
            if(beta <= alpha):
                break
        return max_eval

    def _min_value(self, s, a, alpha, beta):
        """
        Opponent's turn
        Get the minimum of the maximum's value
        """
        # s = [self.internal_board, depth, player_num, opp_num, p_sum, opp_sum]
        # s[1] = s[1] + 1
        # print("min", s[1])
        # print("MIN: ############################")
        if (s[1] >= self.cutoff_depth or (self._is_terminal(s, self.opp_colour))):
            return self._get_eval_score(s, a, self.opp_colour)

        min_val = inf
        actions = self._get_actions(s, self.opp_colour)
        
        for a in actions:
            dist_from_a = 0
            if a[0] == "PLACE":
                dist_from_a = abs(self.n - 1 - a[1] - a[2])
                stolen = 0
            else:
                stolen = 1
            new, num_cap, captured_dist, stolen_dist = self.result(s, a, self.opp_colour)
            if (self.colour == "blue"):
                v = self._max_value([new[0], new[1]+1, new[2] - num_cap + stolen, new[3] + 1 - stolen, new[4] - captured_dist + stolen_dist, new[5] + dist_from_a - stolen_dist], a, alpha, beta)
            else:
                v = self._max_value([new[0], new[1]+1, new[2] - num_cap, new[3]+1, new[4] - captured_dist - stolen_dist, new[5] + dist_from_a + stolen_dist], a, alpha, beta)
            # print("curr board num: ", (s[2], s[3]))
            # print("in the future placing: ", a)
            min_val = min(v, min_val)
            beta = min(beta, v)
            if(beta <= alpha):
                break
        return min_val

    def _is_terminal(self, s, colour):
        """ Do bfs on every starting node of the corresponding colour and check if there is a path to the otherside"""
        # s = [self.internal_board, depth]
        # action = ("PLACE", r, q)
        
        if colour == "red": # red: start is bottom row, goal is top
            starts = [(0,i) for i in range(self.n)]
            goals = [(self.n-1,i) for i in range(self.n)]
        else: # blue: start is left column, goal is right
            starts = [(i,0) for i in range(self.n)]
            goals = [(i,self.n-1) for i in range(self.n)]

        for i in range(self.n):
            node = starts[i]
            if s[0][node[0]][node[1]] == colour:
                if (self.dfs(node[0], node[1], goals, s, colour)):
                    return True
        return False


    def bfs(self, r, q, goals, s):
        visited = [(r,q)]
        queue = [(r,q)]
        while (queue != []):
            curr = queue.pop(0)
            if curr in goals:
                return True
            for neighbour in self.get_neighbours(curr[0], curr[1], s):
                if neighbour not in visited:
                    queue.append(neighbour)
                    visited.append(neighbour)
        return False

    
    def dfs(self, r, q, goals, s, colour):
        visited = [(r,q)]
        stack = [(r,q)]
        while (stack != []):
            curr = stack.pop()
            visited.append(curr)
            if curr in goals:
                return True
            for neighbour in self.get_neighbours(curr[0], curr[1], s, colour):
                if neighbour not in visited:
                    stack.append(neighbour)
                    visited.append(neighbour)
        return False


    def get_neighbours(self, r, q, s, colour):
        firsts = [r+1, r-1, r, r, r+1, r-1]
        seconds = [q, q, q+1, q-1, q-1, q+1]
        neighbours = []
        for i in range(len(firsts)):
            if (firsts[i] < self.n and seconds[i] < self.n and firsts[i] >= 0 and seconds[i] >= 0 and s[0][firsts[i]][seconds[i]] == colour):
                neighbours.append((firsts[i], seconds[i]))
        return neighbours


    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # put your code here
        # Return The Max value among all minimised value

        player_num = self.player_pieces_num
        opp_num = self.opp_pieces_num
        depth = 0
        p_sum = self.player_sum
        opp_sum = self.opp_sum
        s = [self.internal_board, depth, player_num, opp_num, p_sum, opp_sum]
        actions = self._get_actions(s, self.colour)

        # Line below is taking forever
        alpha = -inf
        beta = inf
        values = []
        
        for a in actions:
            new, num_cap, captured_dist, stolen_dist = self.result(s,a, self.colour)
            dist_from_a = 0
            if a[0] == "PLACE":
                dist_from_a = abs(self.n - 1 - a[1] - a[2])
                stolen = 0
            else:
                stolen = 1
            
            if self.colour == "blue":
                values.append(self._min_value([new[0], new[1]+1, new[2]+1+stolen, new[3]-num_cap-stolen, new[4] + dist_from_a + stolen_dist,  new[5] - captured_dist - stolen_dist], a, alpha, beta))
            else:
                values.append(self._min_value([new[0], new[1]+1, new[2]+1, new[3]-num_cap, new[4] + dist_from_a - stolen_dist,  new[5] - captured_dist + stolen_dist], a, alpha, beta))
            # print("doing action: ", a, "yields an evaluation score of", self._get_eval_score([new[0], new[1]+1, new[2]+1, new[3]-num_cap, p_sum + dist_from_a, opp_sum - captured_dist], a))
        # print("Process finished --- %s seconds ---" % (time.time() - start_time))
        
        max_value = max(values)
        action = actions[values.index(max_value)]
        return action

    
    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of 
        their chosen action. Update your internal representation of the 
        game state based on this. The parameter action is the chosen 
        action itself. 
        
        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """
        self.last_action = action
        if(self.is_first_turn):
            self.first_turn = self.last_action
            self.is_first_turn = False
            self.is_blues_first_turn = True
        if (self.is_first_turn == False and player == "blue"):
            self.is_blues_first_turn = False

        if (self.last_action[0] == "PLACE"):
            self.internal_board[self.last_action[1]][self.last_action[2]] = player
            cap, sum_dist_from_center = self.apply_capture(self.internal_board, player, (self.last_action[1], self.last_action[2]))
            if (player == self.colour):
                self.player_pieces_num += 1
                self.opp_pieces_num -= cap
                self.player_sum += abs(self.n - 1 - action[1] - action[2])
                self.opp_sum -= sum_dist_from_center
            else:
                self.opp_pieces_num += 1
                self.player_pieces_num -= cap
                self.opp_sum += abs(self.n - 1 - action[1] - action[2])
                self.player_sum -= sum_dist_from_center
        elif (self.last_action[0] == "STEAL"):
            is_stealCoord_reached = False
            steal_coord = tuple()
            for i in range(self.n):
                if is_stealCoord_reached:
                    break
                for j in range(self.n):
                    if self.internal_board[i][j] == "red":
                        self.internal_board[i][j] = 0
                        steal_coord = (i,j)
                        is_stealCoord_reached = True
                        break
            self.internal_board[steal_coord[1]][steal_coord[0]] = "blue"
        self.cutoff_depth = self._get_cutoff_depth(self.player_pieces_num, self.opp_pieces_num)
        

        # print("BOARD: ", self.internal_board)


    def apply_capture(self, board, player, coord):
        if (player == "red"):
            opp = "blue"
        else:
            opp = "red"
        captured = set()
        
        # Check each capture pattern intersecting with coord
        for pattern in _CAPTURE_PATTERNS:
            coords = [_ADD(coord, s) for s in pattern]
            # No point checking if any coord is outside the board!
            if all(map(self.inside_bounds, coords)):
                tokens = [board[coord[0]][coord[1]] for coord in coords]
                if tokens == [player, opp, opp]:
                    # Capturing has to be deferred in case of overlaps
                    # Both mid cell tokens should be captured
                    captured.update(coords[1:])

        # Remove any captured tokens
        sum_dist_from_center = 0
        for coord in captured:
            board[coord[0]][coord[1]] = 0
            sum_dist_from_center += abs(self.n - 1 - coord[0] - coord[1])
        return len(captured), sum_dist_from_center


    def inside_bounds(self, coord):
        """
        True iff coord inside board bounds.
        Note: code borrowed from referee
        """
        r, q = coord
        return r >= 0 and r < self.n and q >= 0 and q < self.n