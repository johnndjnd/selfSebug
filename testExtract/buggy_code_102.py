def choose_num(x, y):
    if x > y:
        return -1
    if y % 2 == 0:
        return y
    if x == y:
        return -1
    return x - 1


def choose_num(x, y):
    x1 = x > y
    if x1:
        x2 = -1
        return x2
    x3 = y % 2
    x4 = x3 == 0
    if x4:
        return y
    x5 = x == y
    if x5:
        x6 = -1
        return x6
    x7 = x - 1
    return x7