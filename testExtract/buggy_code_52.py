def below_threshold(l: list, t: int):
    for e in l:
        if e >= t:
            return True
    return False


def below_threshold(l: list, t: int):
    for e in l:
        x1 = e >= t
        if x1:
            return True
    return False