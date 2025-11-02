def derivative(xs: list):
    return [(i * x) for i, x in enumerate(xs)]


def derivative(xs: list):
    x1 = []
    x2 = enumerate(xs)
    for i, x in x2:
        x3 = i * x
        x1.append(x3)
    return x1