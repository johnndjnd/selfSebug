def triples_sum_to_zero(l: list):
    for i in range(1, len(l)):
        for j in range(i + 1, len(l)):
            for k in range(j + 1, len(l)):
                if l[i] + l[j] + l[k] == 0:
                    return True
    return False


def triples_sum_to_zero(l: list):
    x1 = len(l)
    x2 = range(1, x1)
    for i in x2:
        x3 = i + 1
        x4 = len(l)
        x5 = range(x3, x4)
        for j in x5:
            x6 = j + 1
            x7 = len(l)
            x8 = range(x6, x7)
            for k in x8:
                x9 = l[i]
                x10 = l[j]
                x11 = x9 + x10
                x12 = l[k]
                x13 = x11 + x12
                x14 = x13 == 0
                if x14:
                    return True
    return False