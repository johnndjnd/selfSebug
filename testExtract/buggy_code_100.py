def make_a_pile(n):
    return [n + 2*i + i for i in range(n)]


def make_a_pile(n):
    x1 = []
    x2 = range(n)
    for i in x2:
        x3 = 2 * i
        x4 = n + x3
        x5 = x4 + i
        x1.append(x5)
    return x1