import pytest
def magic(square):
    n = 3
    # missing data
    for i in range(0, n):
        if len(square[i]) != n:
            return "Invalid data: missing or repeated number"
    
    for i in range(1, n):
        for j in range(1, n):
            if square[i - 1][j - 1] == square[i][j]:
                return "Invalid data: missing or repeated number"


    diagon_sum1 = 0
    diagon_sum2 = 0
    for i in range(0, n):
        diagon_sum1 += square[i][i]
    for i in range (0, n):
        diagon_sum2 += square[i][i]
    if diagon_sum1 != diagon_sum2:
        return ("Not a magic square")

    for i in range(0, n):
        row_sum = 0
        for j in range(0, n):
            row_sum += square[i][j]
        if row_sum != diagon_sum1:
            return ("Not a magic square")
            
    for i in range(0, n):
        col_sum = 0
        for j in range(0, n):
            col_sum += square[j][i]
        if col_sum != diagon_sum1:
            return ("Not a magic square")

    return ("Magic square")
print(magic([[1, 2], [3, 4, 5], [6, 7, 8]]))
            
