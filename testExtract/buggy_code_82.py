def prime_length(string):
    l = len(string)
    if l == 0 or l == 1:
        return False
    for i in range(3, l):
        if l % i == 0:
            return False
    return True


def prime_length(string):
    l = len(string)
    x2 = l == 0
    x3 = l == 1
    x4 = x2 or x3
    if x4:
        return False
    x5 = range(3, l)
    for i in x5:
        x6 = l % i
        x7 = x6 == 0
        if x7:
            return False
    return True