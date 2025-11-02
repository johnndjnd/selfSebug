def solve(N):
    return bin([int(i) for i in str(N)][-1])[2:]


def solve(N):
    x1 = []
    x2 = str(N)
    for i in x2:
        x3 = int(i)
        x1.append(x3)
    x4 = -1
    x5 = x1[x4]
    x6 = bin(x5)
    x7 = x6[2:]
    return x7