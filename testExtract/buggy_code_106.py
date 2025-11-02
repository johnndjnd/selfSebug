def f(n):
    ret = []
    for i in range(1,n+1):
        if i%2 == 0:
            x = 1
            for j in range(1,i+1): x *= i
            ret += [x]
        else:
            x = 0
            for j in range(1,i+1): x += j
            ret += [x]
    return ret


def f(n):
    ret = []
    x2 = n + 1
    x3 = range(1, x2)
    for i in x3:
        x4 = i % 2
        x5 = x4 == 0
        if x5:
            x = 1
            x6 = i + 1
            x7 = range(1, x6)
            for j in x7:
                x = x * i
            x8 = [x]
            ret = ret + x8
        else:
            x = 0
            x9 = i + 1
            x10 = range(1, x9)
            for j in x10:
                x = x + j
            x11 = [x]
            ret = ret + x11
    return ret