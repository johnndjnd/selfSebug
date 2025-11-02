def iscube(a):
    a = abs(a)
    return int(round(a ** (1. / 3))) == a


def iscube(a):
    a = abs(a)
    x2 = 1. / 3
    x3 = a ** x2
    x4 = round(x3)
    x5 = int(x4)
    x6 = x5 == a
    return x6