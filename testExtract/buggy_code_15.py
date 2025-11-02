def string_sequence(n: int) -> str:
    return ' '.join([str(x) for x in range(n)])


def string_sequence(n: int):
    x1 = []
    x2 = range(n)
    for x in x2:
        x3 = str(x)
        x1.append(x3)
    x4 = ' '.join(x1)
    return x4