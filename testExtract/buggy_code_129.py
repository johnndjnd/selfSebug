def minPath(grid, k):
    n = len(grid)
    val = n * n + 1
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                temp = []
                if i != 0:
                    temp.append(grid[i][j])

                if j != 0:
                    temp.append(grid[i][j])

                if i != n - 1:
                    temp.append(grid[i][j])

                if j != n - 1:
                    temp.append(grid[i][j])

                val = min(temp)

    ans = []
    for i in range(k):
        if i % 2 == 0:
            ans.append(1)
        else:
            ans.append(val)
    return ans


def minPath(grid, k):
    n = len(grid)
    x2 = n * n
    val = x2 + 1
    x4 = range(n)
    for i in x4:
        x5 = range(n)
        for j in x5:
            x6 = grid[i]
            x7 = x6[j]
            x8 = x7 == 1
            if x8:
                temp = []
                x10 = i != 0
                if x10:
                    x11 = grid[i]
                    x12 = x11[j]
                    temp.append(x12)
                x13 = j != 0
                if x13:
                    x14 = grid[i]
                    x15 = x14[j]
                    temp.append(x15)
                x16 = n - 1
                x17 = i != x16
                if x17:
                    x18 = grid[i]
                    x19 = x18[j]
                    temp.append(x19)
                x20 = n - 1
                x21 = j != x20
                if x21:
                    x22 = grid[i]
                    x23 = x22[j]
                    temp.append(x23)
                val = min(temp)
    ans = []
    x26 = range(k)
    for i in x26:
        x27 = i % 2
        x28 = x27 == 0
        if x28:
            ans.append(1)
        else:
            ans.append(val)
    return ans