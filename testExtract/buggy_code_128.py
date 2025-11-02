def prod_signs(arr):
    if not arr: return None
    prod = 0 if 0 in arr else (-1) ** 2 * len(list(filter(lambda x: x < 0, arr)))
    return prod * sum([abs(i) for i in arr])


def prod_signs(arr):
    x1 = not arr
    if x1:
        return None
    x2 = 0 in arr
    x3 = -1
    x4 = x3 ** 2
    x5 = lambda x: x < 0
    x6 = filter(x5, arr)
    x7 = list(x6)
    x8 = len(x7)
    x9 = x4 * x8
    prod = 0 if x2 else x9
    x11 = []
    for i in arr:
        x12 = abs(i)
        x11.append(x12)
    x13 = sum(x11)
    x14 = prod * x13
    return x14