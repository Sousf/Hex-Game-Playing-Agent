from cmath import inf
from random import randint


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
        rows, cols = (self.n, self.n)
        self.internal_board = [[0 for i in range(cols)] for j in range(rows)]
        self.is_first_turn = True
        self.cutoff_depth = 3


    def _get_eval_score(s):
        # Capturing opponent's pieces gets positive score

        # Forming a chain get a positive score

        # Getting closer to the opposit side gets a positive score

        # each turn taken incur a -1 penalty
        return 0

    def _get_actions(s):
        """
        Get all possible actions at the current state
        """
        pass

    def _max_value(self, s):
        """
        Player's turn
        Get the maximum of the minimum values
        """

        # s = (self.internal_board, depth)
        if (s[1] == self.cutoff_depth):
            return _get_eval_score(s)

        v = -inf
        for a in _get_actions(s):
            v = max(v, _min_value(result(s, a)))
        return v

    def result(s, a):
        """
        s: is the current internal board state
        a: the action we want to apply to the state

        return updated state with action a.
        """
        pass

    def _min_value(self, s):
        """
        Opponent's turn
        Get the minimum of the maximum's value
        """
        # s = ("PLACE", r, q, depth)
        if (s[3] == self.cutoff_depth):
            return _get_eval_score(s)


        v = inf
        for a in _get_actions(s):
            v = min(v, _min_value(result(s, a)))
        return v

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # put your code here
        # Return The Max value among all minimised value

        
        depth = 0
        s = (self.internal_board, depth)
        actions = _get_actions(s)
        values = [_get_eval_score(result(s,a)) for a in actions]
        
        max_value = max(values)
        action = actions[values.index(max_value)]
            
        # r = randint(0,self.n-1)
        # q = randint(0,self.n-1)
        # action = ("PLACE", r, q)
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
        # put your code here
        if (self.last_action[0] == "PLACE"):
            self.internal_board[self.last_action[1]][self.last_action[2]] = player
        else:
            if (player == "blue"):
                self.internal_board[self.first_turn[1]][self.first_turn[2]] = "red"
            else:
                self.internal_board[self.first_turn[1]][self.first_turn[2]] = "blue"

        print("BOARD: ", self.internal_board)


