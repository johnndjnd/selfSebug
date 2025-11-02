def pluck(arr):
    if(len(arr) == 0): return []
    evens = list(filter(lambda x: x%2 == 0, arr))
    if(evens == []): return []
    return [arr.index(min(evens)), min(evens)]


def pluck(arr):
    x1 = len(arr)
    x2 = x1 == 0
    if x2:
        x3 = []
        return x3
    x4 = lambda x: x%2 == 0
    x5 = filter(x4, arr)
    evens = list(x5)
    x7 = []
    x8 = evens == x7
    if x8:
        x9 = []
        return x9
    x10 = min(evens)
    x11 = arr.index(x10)
    x12 = min(evens)
    x13 = [x11, x12]
    return x13