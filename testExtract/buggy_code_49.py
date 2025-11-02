def modp(n: int, p: int):
    ret = 0
    for i in range(n):
        ret = (2 * ret) % p
    return ret


def modp(n: int, p: int):
    ret = 0
    x1 = range(n)
    for i in x1:
        x2 = 2 * ret
        ret = x2 % p
    return ret