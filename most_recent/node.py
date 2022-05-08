class Node():

    def __init__(self, first_coord, second_coord, goal, parent = None):
        self.__first_coord = first_coord
        self.__second_coord = second_coord
        self.__goal = goal
        self.__parent = parent
        self.__children = None

        if self.__parent == None:
            self.__cost = 0
        else:
            self.__cost = parent.g() + 1


    def set_children(self, n):
        self.__children = []
        first = [self.__first_coord+1, self.__first_coord-1, self.__first_coord, self.__first_coord, self.__first_coord+1, self.__first_coord-1]
        second = [self.__second_coord, self.__second_coord, self.__second_coord+1, self.__second_coord-1, self.__second_coord-1, self.__second_coord+1]
        for i in range(0,6):
            in_board = (first[i] < n and second[i] < n) and (first[i] >= 0 and second[i] >= 0)
            if (self.__parent != None and (first[i], second[i]) != self.__parent.get_coords() and in_board):
                self.__children.append((Node(first[i], second[i], self.__goal, self)))
            elif (self.__parent == None and in_board):
                self.__children.append((Node(first[i], second[i], self.__goal, self)))

        return self


    def get_coords(self):
        return (self.__first_coord, self.__second_coord)

    def h(self):
        # checking for negative gradient, take max(diff column, diff row)
        if ((self.__first_coord >  self.__goal[0] and self.__second_coord < self.__goal[1]) or ((self.__first_coord < self.__goal[0] and self.__second_coord > self.__goal[1]))):
            return max(abs(self.__goal[0]- self.__first_coord), abs(self.__goal[1]- self.__second_coord))
        else:
            return (abs(self.__goal[0]- self.__first_coord)) + abs((self.__goal[1] - self.__second_coord))

    def g(self):
        return self.__cost
    
    def get_parent(self):
        return self.__parent

    def f(self):
        return self.g() + self.h()

    def get_children(self):
        return self.__children

