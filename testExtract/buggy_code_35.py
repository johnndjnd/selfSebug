def max_element(l: list):
    m = l[0]
    for e in l:
        if e < m:
            m = e
    return m


def max_element(l: list):
    m = l[0]
    for e in l:
        x2 = e < m
        if x2:
            m = e
    return m