def simplify(x, n):
    a, b = x.split("/")
    c, d = n.split("/")
    a = int(b) * int(c)
    d = int(c) * int(b)
    numerator = int(a) * int(c)
    denom = int(b) * int(d)
    if (numerator/denom == int(numerator/denom)):
        return True
    return False


def simplify(x, n):
    x1 = x.split("/")
    a, b = x1
    x2 = n.split("/")
    c, d = x2
    x3 = int(b)
    x4 = int(c)
    a = x3 * x4
    x6 = int(c)
    x7 = int(b)
    d = x6 * x7
    x9 = int(a)
    x10 = int(c)
    numerator = x9 * x10
    x12 = int(b)
    x13 = int(d)
    denom = x12 * x13
    x15 = numerator / denom
    x16 = numerator / denom
    x17 = int(x16)
    x18 = x15 == x17
    if x18:
        return True
    return False