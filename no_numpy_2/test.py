from cmath import inf
import copy
from random import randint
from numpy import zeros, array, roll, vectorize, average



# borrowed from referee
_ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])
_HEX_STEPS = array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
    dtype="i,i")
_CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
    for n1, n2 in 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1))) + 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 2)))]


print(_CAPTURE_PATTERNS)

import sys
n=8
rows, cols = (n, n)
internal_board = [["r" for i in range(cols)] for j in range(rows)]

print(sys.getsizeof(internal_board))
print(average([]))