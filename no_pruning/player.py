from cmath import inf
import copy
from random import randint
import time
from numpy import average, zeros, array, roll, vectorize



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
        self.cutoff_depth = 3


    def _get_eval_score(self, s, a):

        # Forming a chain get a positive score

        # find shortest path between start and last_coord

        # find the shortest path between last_coord and goal


        # Having more of our own colour gets rewarded
        same_colour = 0
        opponent_colour = 0
        opponent_pieces = []
        dists_self = []
        dists_opponent = []
        for i in range(0, self.n):
            for j in range(0,self.n):
                if(s[0][i][j] == self.colour):
                    same_colour += 1
                    dists_self.append(abs(self.n - 1 - i - j))
                elif (s[0][i][j] != self.colour and s[0][i][j] != 0):
                    opponent_colour += 1
                    opponent_pieces.append((i,j))
                    dists_opponent.append(abs(self.n - 1 - i - j))

        dist_from_diag_diff = -(average(dists_self) - average(dists_opponent))

        eval_score = 0.5*(same_colour - opponent_colour) + 0.2*(dist_from_diag_diff)

        # eval_score = 0.5*(same_colour - opponent_colour) 
        # assert(eval_score >= 0)
        return eval_score

    def _get_actions(self, s):
        """
        Get all possible actions at the current state
        """
        # action = ("PLACE", r, q)
        actions = []
        for i in range(self.n):
            for j in range(self.n):
                if (s[0][i][j] == 0):
                    actions.append(("PLACE", i, j))
        # need to add aciton for steal??
        if (self.is_first_turn and self.colour == "blue"):
            actions.append(("STEAL", ))

        if (self.is_first_turn and self.colour == "red" and (("PLACE", (self.n-1)/2, (self.n-1)/2) in actions)):
            actions.remove(("PLACE", (self.n-1)/2, (self.n-1)/2))
        return actions

    def result(self, s, a, colour):
        """
        s: is the current internal board state
        a: the action we want to apply to the state
        return updated state with action a.
        """
        new_state = copy.deepcopy(s[0])

        if (a[0] == "PLACE"):
            new_state[a[1]][a[2]] = colour
            self.apply_capture(new_state, colour, (a[1], a[2]))
        elif (a[0] == "STEAL"):
            # TODO: CHECK THIS
            new_state[self.a[1]][a[2]] = 0
            if (self.colour == "blue"):
                new_state[a[2]][a[1]] = "blue" 
            else:
                new_state[a[2]][a[1]] = "red" 
        # ANOTHER CASE: capture rule

        return new_state

    def _max_value(self, s,a):
        """
        Player's turn
        Get the maximum of the minimum values
        """
        # s = [self.internal_board, depth]
        # s[1] += 1
        # print("max", s[1])
        if (s[1] == self.cutoff_depth or (self._is_terminal(s))):
            return self._get_eval_score(s, a)

        max_eval = -inf
        for a in self._get_actions(s):
            v = self._min_value([self.result(s, a, self.colour), s[1]+1], a)
            max_eval = max(v, max_eval)
        return max_eval

    def _min_value(self, s, a):
        """
        Opponent's turn
        Get the minimum of the maximum's value
        """
        # s = [self.internal_board, depth]
        # s[1] = s[1] + 1
        # print("min", s[1])
        if (s[1] == self.cutoff_depth or (self._is_terminal(s))):
            return self._get_eval_score(s, a)

        min_val = inf
        for a in self._get_actions(s):
            v = self._max_value([self.result(s, a, self.opp_colour), s[1]+1], a)
            min_val = min(v, min_val)
        return min_val

    def _is_terminal(self, s):
        """ Do bfs on every starting node of the corresponding colour and check if there is a path to the otherside"""
        # s = [self.internal_board, depth]
        # action = ("PLACE", r, q)
        
        if self.colour == "red": # red: start is bottom row, goal is top
            starts = [(0,i) for i in range(self.n)]
            goals = [(self.n-1,i) for i in range(self.n)]
        else: # blue: start is left column, goal is right
            starts = [(i,0) for i in range(self.n)]
            goals = [(i,self.n-1) for i in range(self.n)]

        for i in range(self.n):
            node = starts[i]
            if s[0][node[0]][node[1]] == self.colour:
                if (self.bfs(node[0], node[1], goals, s)):
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


    def get_neighbours(self, r, q, s):
        firsts = [r+1, r-1, r, r, r+1, r-1]
        seconds = [q, q, q+1, q-1, q-1, q+1]
        neighbours = []
        for i in range(len(firsts)):
            if (firsts[i] < self.n and seconds[i] < self.n and firsts[i] >= 0 and seconds[i] >= 0 and s[0][firsts[i]][seconds[i]] == self.colour):
                neighbours.append((firsts[i], seconds[i]))
        return neighbours


    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # put your code here
        # Return The Max value among all minimised value
        
        depth = 0
        s = [self.internal_board, depth]
        actions = self._get_actions(s)

        # Line below is taking forever
        alpha = -inf
        beta = inf
        values = []
        # values = [self._max_value([self.result(s,a, self.colour), s[1]+1], a, alpha, beta) for a in actions]
        for a in actions:
            values.append(self._min_value([self.result(s,a, self.colour), s[1]+1], a))
        # values = [self._min_value([self.result(s,a, self.colour), s[1]+1], a, alpha, beta) for a in actions]
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

        if (self.last_action[0] == "PLACE"):
            self.internal_board[self.last_action[1]][self.last_action[2]] = player
            self.apply_capture(self.internal_board, player, (self.last_action[1], self.last_action[2]))
        elif (self.last_action[0] == "STEAL"):
            self.internal_board[self.first_turn[1]][self.first_turn[2]] = 0
            if (player == "blue"):
                self.internal_board[self.first_turn[2]][self.first_turn[1]] = "blue"
            else:
                self.internal_board[self.first_turn[2]][self.first_turn[1]] = "red"


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
        for coord in captured:
            board[coord[0]][coord[1]] = 0


    def inside_bounds(self, coord):
        """
        True iff coord inside board bounds.
        Note: code borrowed from referee
        """
        r, q = coord
        return r >= 0 and r < self.n and q >= 0 and q < self.n