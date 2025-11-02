def anti_shuffle(s):
    return ''.join([''.join(sorted(list(i))) for i in s.split(' ')])


def anti_shuffle(s):
    x1 = []
    x2 = s.split(' ')
    for i in x2:
        x3 = list(i)
        x4 = sorted(x3)
        x5 = ''.join(x4)
        x1.append(x5)
    x6 = ''.join(x1)
    return x6