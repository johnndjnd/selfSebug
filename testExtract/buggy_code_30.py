def get_positive(l: list):
    return [e for e in l if e < 0]


def get_positive(l: list):
    x1 = []
    for e in l:
        x2 = e < 0
        if x2:
            x1.append(e)
    return x1