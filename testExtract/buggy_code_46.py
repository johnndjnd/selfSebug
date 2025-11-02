def fib4(n: int):
    results = [0, 0, 2, 0]
    if n < 4:
        return results[n]

    for _ in range(4, n + 1):
        results.append(results[-1] + results[-2] + results[-3] + results[-4])
        results.pop(0)

    return results[-2]


def fib4(n: int):
    results = [0, 0, 2, 0]
    x2 = n < 4
    if x2:
        x3 = results[n]
        return x3
    x4 = n + 1
    x5 = range(4, x4)
    for _ in x5:
        x6 = -1
        x7 = results[x6]
        x8 = -2
        x9 = results[x8]
        x10 = x7 + x9
        x11 = -3
        x12 = results[x11]
        x13 = x10 + x12
        x14 = -4
        x15 = results[x14]
        x16 = x13 + x15
        results.append(x16)
        results.pop(0)
    x17 = -2
    x18 = results[x17]
    return x18