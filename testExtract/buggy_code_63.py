def fibfib(n: int):
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 2
    return fibfib(n - 1) + fibfib(n - 2) + fibfib(n - 3)


def fibfib(n: int):
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
    x5 = fibfib(x4)
    x6 = n - 2
    x7 = fibfib(x6)
    x8 = x5 + x7
    x9 = n - 3
    x10 = fibfib(x9)
    x11 = x8 + x10
    return x11