def will_it_fly(q,w):
    if sum(q) > w:
        return False

    i, j = 0, len(q)-1
    while i<j:
        if q[i] == q[j]:
            return False
        i+=1
        j-=1
    return True


def will_it_fly(q,w):
    x1 = sum(q)
    x2 = x1 > w
    if x2:
        return False
    x3 = len(q)
    x4 = x3 - 1
    x5 = (0, x4)
    i, j = x5
    while True:
        x6 = i < j
        if not x6:
            break
        x7 = q[i]
        x8 = q[j]
        x9 = x7 == x8
        if x9:
            return False
        i = i + 1
        j = j - 1
    return True