def multiply(a, b):
    return abs(a % 10) * abs(b % 10) * a * b


def multiply(a, b):
    x1 = a % 10
    x2 = abs(x1)
    x3 = b % 10
    x4 = abs(x3)
    x5 = x2 * x4
    x6 = x5 * a
    x7 = x6 * b
    return x7