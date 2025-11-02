import math


def poly(xs: list, x: float):
    """
    Evaluates polynomial with coefficients xs at point x.
    return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
    """
    return sum([coeff * math.pow(x, i) for i, coeff in enumerate(xs)])


def find_zero(xs: list):
    begin, end = -1., 1.
    while poly(xs, begin) * poly(xs, end) > 0:
        begin *= 2.0
        end *= 2.0
    while begin - end > 1e-10:
        center = (begin + end) / 2.0
        if poly(xs, center) * poly(xs, begin) > 0:
            begin = center
        else:
            end = center
    return begin


import math   # 未分解语句
def poly(xs: list, x: float):
    x1 = []
    x2 = enumerate(xs)
    for i, coeff in x2:
        x3 = math.pow(x, i)
        x4 = coeff * x3
        x1.append(x4)
    x5 = sum(x1)
    return x5
def find_zero(xs: list):
    x6 = -1.
    x7 = (x6, 1.)
    begin, end = x7
    while True:
        x8 = poly(xs, begin)
        x9 = poly(xs, end)
        x10 = x8 * x9
        x11 = x10 > 0
        if not x11:
            break
        begin = begin * 2.0
        end = end * 2.0
    while True:
        x12 = begin - end
        x13 = x12 > 1e-10
        if not x13:
            break
        x14 = begin + end
        center = x14 / 2.0
        x16 = poly(xs, center)
        x17 = poly(xs, begin)
        x18 = x16 * x17
        x19 = x18 > 0
        if x19:
            begin = center
        else:
            end = center
    return begin