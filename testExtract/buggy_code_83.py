def starts_one_ends(n):
    if n == 1: return 1
    return 18 * n * (10 ** (n - 2))


def starts_one_ends(n):
    x1 = n == 1
    if x1:
        return 1
    x2 = 18 * n
    x3 = n - 2
    x4 = 10 ** x3
    x5 = x2 * x4
    return x5