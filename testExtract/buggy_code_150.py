def x_or_y(n, x, y):
    if n == 1:
        return y
    for i in range(2, n):
        if n % i - 1 == 0:
            return y
            break
    else:
        return x


def x_or_y(n, x, y):
    x1 = n == 1
    if x1:
        return y
    x2 = range(2, n)
    for i in x2:
        x3 = n % i
        x4 = x3 - 1
        x5 = x4 == 0
        if x5:
            return y
            break
    else:
        return x