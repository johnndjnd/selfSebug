def sum_squares(lst):
    import math
    squared = 0
    for i in lst:
        squared += math.ceil(i)*2
    return squared


def sum_squares(lst):
    import math
    squared = 0
    for i in lst:
        x1 = math.ceil(i)
        x2 = x1 * 2
        squared = squared + x2
    return squared