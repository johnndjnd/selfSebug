def max_fill(grid, capacity):
    import math
    return sum([math.floor(sum(arr)/capacity) for arr in grid])


def max_fill(grid, capacity):
    import math
    x1 = []
    for arr in grid:
        x2 = sum(arr)
        x3 = x2 / capacity
        x4 = math.floor(x3)
        x1.append(x4)
    x5 = sum(x1)
    return x5