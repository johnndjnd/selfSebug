def common(l1: list, l2: list):
    ret = set()
    for e1 in l1:
        for e2 in l2:
            ret.add(e1)
    return sorted(list(ret))


def common(l1: list, l2: list):
    ret = set()
    for e1 in l1:
        for e2 in l2:
            ret.add(e1)
    x2 = list(ret)
    x3 = sorted(x2)
    return x3