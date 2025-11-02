def monotonic(l: list):
    if l == sorted(l) or l == sorted(l, reverse=True):
        return False
    return True


def monotonic(l: list):
    x1 = sorted(l)
    x2 = l == x1
    x3 = sorted(l, reverse=True)
    x4 = l == x3
    x5 = x2 or x4
    if x5:
        return False
    return True