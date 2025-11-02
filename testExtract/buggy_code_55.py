def fib(n: int):
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 2
    return fib(n - 1) + fib(n - 2)


def fib(n: int):
    x1 = n == 0
    if x1:
        return 0
    x2 = n == 1
    if x2:
        return 1
    x3 = n == 2
    if x3:
        return 2
    x4 = n - 1
    x5 = fib(x4)
    x6 = n - 2
    x7 = fib(x6)
    x8 = x5 + x7
    return x8