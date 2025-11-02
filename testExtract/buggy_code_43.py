def pairs_sum_to_zero(l):
    for i, l1 in enumerate(l):
        for j in range(i, len(l)):
            if l1 + l[j] == 0:
                return True
    return False


def pairs_sum_to_zero(l):
    x1 = enumerate(l)
    for i, l1 in x1:
        x2 = len(l)
        x3 = range(i, x2)
        for j in x3:
            x4 = l[j]
            x5 = l1 + x4
            x6 = x5 == 0
            if x6:
                return True
    return False