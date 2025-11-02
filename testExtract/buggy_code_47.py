def median(l: list):
    l = sorted(l)
    if len(l) % 2 == 1:
        return l[len(l) // 2]
    else:
        return (l[len(l) - 1 // 2] + l[len(l) // 2]) / 2.0


def median(l: list):
    l = sorted(l)
    x2 = len(l)
    x3 = x2 % 2
    x4 = x3 == 1
    if x4:
        x5 = len(l)
        x6 = x5 // 2
        x7 = l[x6]
        return x7
    else:
        x8 = len(l)
        x9 = 1 // 2
        x10 = x8 - x9
        x11 = l[x10]
        x12 = len(l)
        x13 = x12 // 2
        x14 = l[x13]
        x15 = x11 + x14
        x16 = x15 / 2.0
        return x16